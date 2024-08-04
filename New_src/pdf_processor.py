# pdf_processor.py
import logging
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm
from typing import Dict, Any
from unstructured.partition.pdf import partition_pdf

from New_src.Config import load_config
from New_src.utils import extract_year_from_filename, extract_entity_name, get_output_folder, is_already_processed, \
    copy_pdf_to_output
from New_src.element_processor import process_elements
from New_src.file_handler import (
    save_elements_data, save_metadata_json, save_metadata_html, save_tables,
    load_error_files, update_error_log, generate_summary_report
)

class PDFProcessingError(Exception):
    """Custom exception for PDF processing errors."""

    def __init__(self, message: str, file_path: str, original_error: Exception = None):
        self.message = message
        self.file_path = file_path
        self.original_error = original_error
        super().__init__(self.message)

    def __str__(self):
        return f"Error processing {self.file_path}: {self.message}"

class PDFProcessor:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger('pdf_processor')
        self.error_log_file = Path(self.config['output_dir']) / 'error_log.json'
        self.error_files = load_error_files(self.error_log_file)

    def process_pdfs(self):
        pdf_files = list(Path(self.config['input_dir']).glob('**/*.pdf'))
        successful_files = []
        failed_files = []

        with ProcessPoolExecutor(max_workers=self.config['num_workers']) as executor:
            futures = {executor.submit(self._process_file_with_retry, file_path): file_path for file_path in pdf_files}
            for future in tqdm(as_completed(futures), total=len(futures), desc="Processing PDFs"):
                file_path = futures[future]
                try:
                    result = future.result()
                    if result:
                        successful_files.append(str(file_path))
                    else:
                        failed_files.append(str(file_path))
                except Exception as e:
                    self.logger.error(f"Failed to process {file_path}: {e}")
                    failed_files.append(str(file_path))

        generate_summary_report(successful_files, failed_files, Path(self.config['output_dir']))

    def _process_file_with_retry(self, file_path: Path) -> bool:
        for attempt in range(self.config['retry_attempts']):
            try:
                self._process_file(file_path)
                return True
            except PDFProcessingError as e:
                self.logger.warning(f"Error processing {e.file_path} on attempt {attempt + 1}: {e.message}")
                if e.original_error:
                    self.logger.debug(f"Original error: {str(e.original_error)}")

        self.error_files.append(str(file_path))
        update_error_log(self.error_files, self.error_log_file)
        return False

    def _process_file(self, file_path: Path):
        entity_name = extract_entity_name(file_path)
        year = extract_year_from_filename(file_path.name)
        output_folder = get_output_folder(file_path, Path(self.config['output_dir']))

        self.logger.info(f"Processing file: {file_path}")
        self.logger.info(f"Extracted entity name: {entity_name}, year: {year}")

        if is_already_processed(output_folder):
            self.logger.info(f"Skipping already processed file: {file_path}")
            return

        output_folder.mkdir(parents=True, exist_ok=True)

        try:
            elements = partition_pdf(
                filename=str(file_path),
                strategy='hi_res',
                infer_table_structure=True,
                include_metadata=True,
                include_page_breaks=True,
                extract_images_in_pdf=False,
                ocr_languages=['eng'],
                url=None
            )
        except Exception as e:
            raise PDFProcessingError("Failed to partition PDF", str(file_path), e)

        self.logger.info(f"Finished partitioning file: {file_path}")
        all_elements_df, tables, all_elements_metadata = process_elements(elements)

        save_elements_data(all_elements_df, output_folder)
        save_metadata_json(all_elements_metadata, output_folder)
        save_metadata_html(all_elements_metadata, output_folder)
        save_tables(tables, output_folder)

        copy_pdf_to_output(file_path, output_folder)
        self.logger.info(f"Copied original PDF to output folder: {output_folder}")

    def process_single_file(self, file_path: Path):
        output_folder = file_path.parent

        self.logger.info(f"Processing file: {file_path}")

        try:
            elements = partition_pdf(
                filename=str(file_path),
                strategy='hi_res',
                infer_table_structure=True,
                include_metadata=True,
                include_page_breaks=True,
                extract_images_in_pdf=False,
                ocr_languages=['eng'],
                url=None
            )
        except Exception as e:
            raise PDFProcessingError("Failed to partition PDF", str(file_path), e)

        self.logger.info(f"Finished partitioning file: {file_path}")
        all_elements_df, tables, all_elements_metadata = process_elements(elements)

        save_elements_data(all_elements_df, output_folder)
        save_metadata_json(all_elements_metadata, output_folder)
        #save_metadata_html(all_elements_metadata, output_folder)
        save_tables(tables, output_folder)

        self.logger.info(f"Processed file: {file_path}")
