import logging
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, List

from tqdm import tqdm
from unstructured.partition.pdf import partition_pdf
from unstructured.staging.base import elements_to_json

from element_processor import process_elements
from file_handler import (
    generate_summary_report,
    load_error_files,
    save_elements_data,
    save_metadata_html,
    save_metadata_json,
    save_tables,
    update_error_log,
)
from utils import copy_pdf_to_output, get_output_folder, is_already_processed


class PDFProcessor:
    """A class for processing PDF files."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger('pdf_processor')
        self.error_log_file = Path(self.config['output_dir']) / 'error_log.json'
        self.error_files = load_error_files(self.error_log_file)

    def process_pdfs(self):
        pdf_files = list(Path(self.config['input_dir']).glob('**/*.pdf'))
        successful_files = []
        failed_files = []

        if self.config['parallel_processing']:
            self.logger.info("Parallel processing enabled")
            with ProcessPoolExecutor(max_workers=self.config['num_workers']) as executor:
                futures = []
                for i in range(0, len(pdf_files), self.config['batch_size']):
                    batch = pdf_files[i:i+self.config['batch_size']]
                    futures.append(executor.submit(self._process_batch, batch))
                
                for future in tqdm(as_completed(futures), total=len(futures), desc="Processing PDF batches"):
                    batch_results = future.result()
                    successful_files.extend(batch_results['successful'])
                    failed_files.extend(batch_results['failed'])
        else:
            self.logger.info("Parallel processing disabled")
            for file_path in tqdm(pdf_files, desc="Processing PDFs"):
                result = self._process_file(file_path)
                if result:
                    successful_files.append(str(file_path))
                else:
                    failed_files.append(str(file_path))

        generate_summary_report(successful_files, failed_files, Path(self.config['output_dir']))

    def _process_batch(self, batch: List[Path]) -> Dict[str, List[str]]:
        successful = []
        failed = []
        for file_path in batch:
            result = self._process_file(file_path)
            if result:
                successful.append(str(file_path))
            else:
                failed.append(str(file_path))
        return {'successful': successful, 'failed': failed}

    def _process_file(self, file_path: Path) -> bool:
        try:
            output_dir = Path(self.config['output_dir'])
            pdf_filename = file_path.name

            # Check if the PDF already exists in any subfolder of the output directory
            if self._pdf_exists_in_output(output_dir, pdf_filename):
                self.logger.info(f"Skipping already processed file: {file_path}")
                return True  # Return True to indicate successful handling (skipping)

            output_folder = get_output_folder(file_path, output_dir)
            output_folder.mkdir(parents=True, exist_ok=True)

            elements = partition_pdf(
                filename=str(file_path),
                strategy='hi_res',
                hi_res_model_name="yolox",
                infer_table_structure=True,
                include_metadata=True,
                include_page_breaks=True,
                extract_images_in_pdf=False,
                ocr_languages=['eng'],
                use_ocr_for_pages_with_text=False,
                max_partition=1000,  # Adjust based on your needs
            )

            all_elements_df, tables, all_elements_metadata = process_elements(elements)

            save_elements_data(all_elements_df, output_folder)
            save_metadata_json(all_elements_metadata, output_folder)
            save_metadata_html(all_elements_metadata, output_folder)
            save_tables(tables, output_folder)

            # Save raw JSON output
            raw_json_path = output_folder / "raw_elements.json"
            elements_to_json(elements, filename=str(raw_json_path))

            copy_pdf_to_output(file_path, output_folder)
            self.logger.info(f"Processed file: {file_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error processing {file_path}: {str(e)}")
            return False

    def _pdf_exists_in_output(self, output_dir: Path, pdf_filename: str) -> bool:
        return any(output_dir.rglob(pdf_filename))

    def _output_files_exist(self, output_folder: Path) -> bool:
        required_files = [
            "elements_data.csv",
            "metadata.json",
            "metadata.html",
            "raw_elements.json",
        ]
        return all((output_folder / file).exists() for file in required_files)

    def process_single_file(self, file_path: Path):
        self._process_file(file_path)