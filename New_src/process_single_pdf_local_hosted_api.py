import os
import yaml
import logging
from pathlib import Path
import pandas as pd
import json
import re
import requests
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm
from typing import Dict, Any, List, Tuple
from collections import defaultdict
import html
from unstructured_client import shared

# Set environment variables for parallel processing
os.environ['UNSTRUCTURED_PARALLEL_MODE_ENABLED'] = 'true'
os.environ['UNSTRUCTURED_PARALLEL_MODE_URL'] = 'http://localhost:8000/general/v0/general'
os.environ['UNSTRUCTURED_PARALLEL_MODE_THREADS'] = '3'
os.environ['UNSTRUCTURED_PARALLEL_MODE_SPLIT_SIZE'] = '1'
os.environ['UNSTRUCTURED_PARALLEL_RETRY_ATTEMPTS'] = '2'

# Define the API endpoint
API_ENDPOINT = 'http://localhost:8000/general/v0/general'


def load_config(config_path: str) -> dict:
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)

    config['input_dir'] = Path(config['input_dir'])
    config['output_dir'] = Path(config['output_dir'])

    return config


def setup_logging(output_dir: Path) -> logging.Logger:
    log_dir = output_dir / 'logs'
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / 'pdf_processing.log'

    logger = logging.getLogger('pdf_processor')
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def extract_year_from_filename(filename: str) -> str:
    match = re.search(r'_(\d{4})_', filename)
    return match.group(1) if match else "0000"


def extract_entity_name(file_path: Path) -> str:
    file_name = file_path.stem
    parts = file_name.split('_')
    return parts[0] if parts else "Unknown"


def get_output_folder(file_path: Path, base_output_dir: Path) -> Path:
    entity_name = extract_entity_name(file_path)
    year = extract_year_from_filename(file_path.name)
    return base_output_dir / f"{entity_name}_{year}"


def is_already_processed(output_folder: Path) -> bool:
    return output_folder.exists() and (output_folder / "elements_data.csv").exists()


def copy_pdf_to_output(source_path: Path, destination_folder: Path):
    destination_path = destination_folder / source_path.name
    destination_path.write_bytes(source_path.read_bytes())


def extract_element_metadata(element: Dict[str, Any]) -> Dict[str, Any]:
    metadata = {
        "id": element.get('id'),
        "text": element.get('text', ''),
        "category": element.get('type', 'Unknown'),
        "filename": element.get('metadata', {}).get('filename'),
        "parent_id": element.get('metadata', {}).get('parent_id'),
        "coordinates": element.get('metadata', {}).get('coordinates'),
        "detection_class_prob": element.get('metadata', {}).get('detection_class_prob'),
        "page_number": element.get('metadata', {}).get('page_number'),
    }

    if metadata["category"].lower() == "table":
        metadata["text_as_html"] = element.get('metadata', {}).get('text_as_html')

    return metadata


def process_elements(elements: List[Dict[str, Any]]) -> Tuple[pd.DataFrame, List[Dict[str, Any]], List[Dict[str, Any]]]:
    all_elements_df = pd.DataFrame()
    tables = []
    all_elements_metadata = []

    for element in elements:
        element_metadata = extract_element_metadata(element)
        all_elements_metadata.append(element_metadata)

        new_row = pd.DataFrame({
            "Page Number": [element_metadata['page_number']],
            "Element ID": [element_metadata['id']],
            "Parent Element": [element_metadata['parent_id']],
            "Coordinates": [element_metadata['coordinates']],
            "Detection Class Probability": [element_metadata['detection_class_prob']],
            "Category": [element_metadata['category']],
            "Text": [element_metadata['text']],
            "Table as HTML": [element_metadata.get('text_as_html')]
        })
        all_elements_df = pd.concat([all_elements_df, new_row], ignore_index=True)

        if element_metadata['category'].lower() == "table":
            tables.append(element)

    return all_elements_df, tables, all_elements_metadata


def save_elements_data(df: pd.DataFrame, output_folder: Path):
    csv_path = output_folder / "elements_data.csv"
    df.to_csv(csv_path, index=False)


def save_metadata_json(metadata: List[Dict[str, Any]], output_folder: Path):
    json_path = output_folder / "all_elements_metadata.json"
    with open(json_path, 'w') as f:
        json.dump(metadata, f, indent=2)


def generate_html_content(pages: Dict[int, List[Dict[str, Any]]]) -> str:
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Document</title>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; }
            .header, .title { font-size: 24px; font-weight: bold; margin-bottom: 20px; }
            .title { font-size: 20px; }
            .narrative-text { margin-bottom: 15px; }
            .table-container { margin-bottom: 20px; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            .page-break { page-break-before: always; margin-top: 30px; }
            .image-container { margin-bottom: 15px; }
            img { max-width: 100%; height: auto; }
        </style>
    </head>
    <body>
    """

    def render_element(elem: Dict[str, Any]) -> str:
        category = elem['category'].lower()
        if category in ['header', 'title']:
            return f'<div class="{category}">{html.escape(elem["text"])}</div>'
        elif category == 'narrativetext':
            return f'<div class="narrative-text">{html.escape(elem["text"])}</div>'
        elif category == 'table':
            table_html = f'<div class="table-container">'
            if elem.get('parent_id'):
                table_html += f'<div class="table-title">{html.escape(elem["parent_id"])}</div>'
            if elem.get('text_as_html'):
                table_html += elem['text_as_html']
            table_html += '</div>'
            return table_html
        elif category == 'image':
            return f'<div class="image-container"><img src="{html.escape(elem.get("src", ""))}" alt="{html.escape(elem["text"])}" /></div>'
        else:
            return f'<div class="{category}">{html.escape(elem["text"])}</div>'

    for page_num, elements in sorted(pages.items()):
        if page_num > 1:
            html_content += '<div class="page-break"></div>'

        html_content += f'<h1>Page {page_num}</h1>'

        for elem in elements:
            if elem['category'] != 'PageBreak':
                html_content += render_element(elem)

    html_content += """
    </body>
    </html>
    """

    return html_content


def save_metadata_html(metadata: List[Dict[str, Any]], output_folder: Path):
    html_path = output_folder / "all_elements_metadata.html"
    pages = defaultdict(list)
    for elem in metadata:
        if elem['category'] == 'PageBreak':
            if pages:
                pages[max(pages.keys())].append(elem)
        else:
            page_num = elem.get('page_number')
            if page_num is not None:
                pages[page_num].append(elem)

    html_content = generate_html_content(pages)

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(html_content)


def save_tables(tables: List[Dict[str, Any]], output_folder: Path):
    grouped_tables = defaultdict(list)
    for table in tables:
        parent_id = table.get('metadata', {}).get('parent_id', 'unknown_parent')
        grouped_tables[parent_id].append(table)

    for parent_id, table_group in grouped_tables.items():
        combined_html_content = ""
        page_numbers = set()

        for i, table in enumerate(table_group):
            table_html = table.get('metadata', {}).get('text_as_html')
            page_number = table.get('metadata', {}).get('page_number', f'unknown_page_{i}')
            page_numbers.add(str(page_number))

            if table_html:
                combined_html_content += f"<h2>Table Part {i + 1} (Page {page_number})</h2>\n{table_html}\n"

                try:
                    tables_df = pd.read_html(table_html)
                    if tables_df:
                        current_df = tables_df[0]
                        current_df["Parent ID"] = parent_id
                        current_df["Page Number"] = page_number

                        csv_filename = f"table_{parent_id}_page{page_number}_part{i + 1}.csv"
                        csv_path = output_folder / csv_filename
                        current_df.to_csv(csv_path, index=False)
                except ValueError as e:
                    print(f"Error parsing HTML table: {str(e)}")

        if combined_html_content:
            html_content = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Combined Table - Parent ID: {html.escape(parent_id)}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; }}
                    h1 {{ color: #333; }}
                    h2 {{ color: #666; }}
                    table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #f2f2f2; }}
                </style>
            </head>
            <body>
                <h1>Combined Table - Parent ID: {html.escape(parent_id)}</h1>
                <p>Pages: {', '.join(sorted(page_numbers))}</p>
                {combined_html_content}
            </body>
            </html>
            """

            html_filename = f"table_{parent_id}_pages{'_'.join(sorted(page_numbers))}.html"
            html_path = output_folder / html_filename
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)


class PDFProcessor:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger('pdf_processor')
        self.error_log_file = Path(self.config['output_dir']) / 'error_log.json'
        self.error_files = self.load_error_files()

    def load_error_files(self) -> List[str]:
        if self.error_log_file.exists():
            try:
                with open(self.error_log_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return []
        return []

    def update_error_log(self):
        with open(self.error_log_file, 'w') as f:
            json.dump(self.error_files, f, indent=2)

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

        self.generate_summary_report(successful_files, failed_files)

    def _process_file_with_retry(self, file_path: Path) -> bool:
        for attempt in range(self.config['retry_attempts']):
            try:
                self._process_file(file_path)
                return True
            except Exception as e:
                self.logger.warning(f"Error processing {file_path} on attempt {attempt + 1}: {e}")

        self.error_files.append(str(file_path))
        self.update_error_log()
        return False

    def _process_file(self, file_path: Path):
        output_folder = get_output_folder(file_path, Path(self.config['output_dir']))

        self.logger.info(f"Processing file: {file_path}")

        if is_already_processed(output_folder):
            self.logger.info(f"Skipping already processed file: {file_path}")
            return

        output_folder.mkdir(parents=True, exist_ok=True)

        elements = self._process_pdf_with_api(file_path)
        self.logger.info(f"Finished processing file: {file_path}")
        all_elements_df, tables, all_elements_metadata = process_elements(elements)

        save_elements_data(all_elements_df, output_folder)
        save_metadata_json(all_elements_metadata, output_folder)
        save_metadata_html(all_elements_metadata, output_folder)
        save_tables(tables, output_folder)

        copy_pdf_to_output(file_path, output_folder)
        self.logger.info(f"Copied original PDF to output folder: {output_folder}")

    def _process_pdf_with_api(self, file_path: Path) -> List[Dict[str, Any]]:
        with open(file_path, 'rb') as pdf_file:
            files = {'files': (file_path.name, pdf_file, 'application/pdf')}
            req = shared.PartitionParameters(
                files=files,
                strategy="hi_res",
                languages=["eng"],
                split_pdf_page=True,
                split_pdf_concurrency_level=self.config['num_workers'],
                ocr_languages=['eng'],
                include_metadata=True,
                include_page_breaks=True,
                extract_images_in_pdf=False
            )
            response = requests.post(API_ENDPOINT, files=files, data=req.__dict__)

            if response.status_code == 200:
                return response.json()
            else:
                response.raise_for_status()

    def generate_summary_report(self, successful_files: List[str], failed_files: List[str]):
        report = f"""
                PDF Processing Summary Report
                ============================
                Total files processed: {len(successful_files) + len(failed_files)}
                Successfully processed: {len(successful_files)}
                Failed to process: {len(failed_files)}

                Failed files:
                {', '.join(failed_files)}
                """

        report_path = Path(self.config['output_dir']) / 'summary_report.txt'
        with open(report_path, 'w') as f:
            f.write(report)

    def main():
        config = load_config('config.yaml')
        logger = setup_logging(config['output_dir'])

        try:
            processor = PDFProcessor(config)
            processor.process_pdfs()
            logger.info("PDF processing completed successfully")
        except Exception as e:
            logger.critical(f"An unexpected error occurred: {e}", exc_info=True)

    if __name__ == "__main__":
        main()