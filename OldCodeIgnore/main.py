import html5lib
import pandas as pd
import io
from get_onedrive_path import get_onedrive_path
import openpyxl
import os
import re
import logging
import pytesseract
from pathlib import Path
from unstructured.partition.pdf import partition_pdf
from io import StringIO
import datetime as dt
from CleanLogs import delete_error_lines, extract_unique_filenames
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing
from tqdm import tqdm
import time


class PDFProcessor:
    def __init__(self, base_path):
        self.base_path = base_path
        self.error_files = self.load_error_files('../Logs/processing_errors.log')
        pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(filename='../Logs/pdf_processing.log', level=logging.INFO,
                            format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def load_error_files(self, log_file_path):
        error_files = set()
        if os.path.exists(log_file_path):
            with open(log_file_path, 'r') as log_file:
                for line in log_file:
                    match = re.search(r'ERROR:root:Failed to process (.*): Error', line)
                    if match:
                        error_files.add(match.group(1))
        return error_files

    def process_pdfs(self):
        pdf_files = []
        for root, dirs, files in os.walk(self.base_path):
            for file in files:
                if file.endswith('.pdf'):
                    file_path = os.path.join(root, file)
                    if "Split_PDFs" not in file_path and file_path not in self.error_files:
                        match = re.search(r'(\d{4})', file)
                        fileyear = match.group(1) if match else "0000"
                        pdf_files.append((file_path, fileyear))
                    else:
                        self.logger.info(f"Skipping file: {file_path}")

        num_workers = multiprocessing.cpu_count()
        self.logger.info(f"Starting processing of {len(pdf_files)} PDF files with {num_workers} workers")

        with ProcessPoolExecutor(max_workers=num_workers) as executor:
            futures = [executor.submit(self.process_file_with_retry, file_path, year) for file_path, year in pdf_files]

            for future in tqdm(as_completed(futures), total=len(pdf_files), desc="Processing PDFs"):
                try:
                    result = future.result()
                    if result:
                        self.logger.info(f"Successfully processed: {result}")
                except Exception as e:
                    self.logger.error(f"Error in parallel processing: {str(e)}")

        self.logger.info("PDF processing completed")

    def process_file_with_retry(self, file_path, year, max_retries=3, delay=5):
        for attempt in range(max_retries):
            try:
                return self.process_file(file_path, year)
            except Exception as e:
                self.logger.warning(f"Attempt {attempt + 1} failed for {file_path}: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(delay)
                else:
                    self.logger.error(f"Failed to process {file_path} after {max_retries} attempts: {str(e)}")
                    return None

    def process_file(self, file_path, year):
        output_folder = Path(file_path).parent / f"Unstructured_Output_{year}"
        elements_data_file = output_folder / "elements_data.csv"
        if elements_data_file.exists():
            self.logger.info(f"Skipping already processed file: {file_path}")
            return file_path

        output_folder.mkdir(exist_ok=True)
        self.logger.info(f"Processing file: {file_path}")

        elements = partition_pdf(file_path, strategy='hi_res', infer_table_structure=True, metadata=True,
                                 include_page_breaks=True, extract_images_in_pdf=False, url=None)

        self.logger.info(f"Finished partitioning file: {file_path}")
        self.process_elements(elements, output_folder)
        return file_path

    def process_elements(self, elements, output_folder):
        all_elements_df = pd.DataFrame()
        tables = []

        for element in elements:
            if element.metadata:
                new_row = pd.DataFrame({
                    "Page Number": [element.metadata.page_number],
                    "Element ID": [element.id],
                    "Coordinates": [element.metadata.coordinates],
                    "Detection Class Probability": [element.metadata.detection_class_prob],
                    "Category": [element.category],
                    "Text": [element.text]
                })
                all_elements_df = pd.concat([all_elements_df, new_row], ignore_index=True)

            if element.category == "Table":
                tables.append(element)

        if not all_elements_df.empty:
            csv_path = output_folder / "elements_data.csv"
            all_elements_df.to_csv(csv_path, index=False)
            self.logger.info(f"Saved elements data to {csv_path}")

        self.save_tables(tables, output_folder)

    def save_tables(self, tables, output_folder):
        for table_element in tables:
            try:
                html_content = table_element.metadata.text_as_html
                page_number = table_element.metadata.page_number
                table_index = table_element.id

                tables_df = pd.read_html(io.StringIO(html_content))
                if tables_df:
                    cell_df = table_element.metadata.table_as_cells
                    temp_df = tables_df[0]
                    temp_df["Page Number"] = page_number
                    temp_df["Parent Element"] = table_element.metadata.parent_id

                    # Save as CSV
                    csv_path = output_folder / f"table_{page_number}_{table_index}.csv"
                    temp_df.to_csv(csv_path, index=False)

                    # Save as HTML
                    html_path = output_folder / f"table_{page_number}_{table_index}.html"
                    temp_df.to_html(html_path, index=False)

                    # Save cell data as CSV
                    cell_csv_path = output_folder / f"table_cells_{page_number}_{table_index}.csv"
                    cell_df.to_csv(cell_csv_path, index=True)

                    self.logger.info(
                        f"Saved table from page {page_number} to {csv_path}, {html_path}, and {cell_csv_path}")
                else:
                    self.logger.info(f"No tables found on page {page_number}")
            except Exception as e:
                self.logger.error(f"Failed to save table from page {page_number}: {str(e)}")


if __name__ == "__main__":
    try:
        delete_error_lines('../Logs/processing_errors.log')
        onedrive_path = get_onedrive_path() + r"\FDD Database\EFD\FDD Database"
        processor = PDFProcessor(onedrive_path)
        processor.process_pdfs()
    except Exception as e:
        logging.critical(f"An unexpected error stopped the processing: {e}")