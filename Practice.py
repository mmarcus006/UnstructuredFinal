import html5lib
import os
import pandas as pd
import io
from pathlib import Path
from unstructured.partition.pdf import partition_pdf
import pytesseract
from get_onedrive_path import get_onedrive_path
import logging

class PDFProcessor:
    def __init__(self, base_path):
        self.base_path = base_path
        pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        logging.basicConfig(filename='processing_errors.log', level=logging.ERROR)
    def process_pdfs(self):
        # Get all PDF files in the directory tree
        for root, dirs, files in os.walk(self.base_path):
            for file in files:
                if file.endswith('.pdf'):
                    self.process_file(os.path.join(root, file))

    def process_file(self, file_path):
        try:
            output_folder = Path(file_path).parent / "Unstructured_Outputs"
            output_folder.mkdir(exist_ok=True)
            try:
                elements = partition_pdf(file_path, strategy='hi_res', infer_table_structure=True, metadata=True,
                                         include_page_breaks=True)
            except Exception as e:
                raise ValueError(f"Error partitioning PDF {file_path}: {e}")

            self.process_elements(elements, output_folder)
        except Exception as e:
            logging.error(f"Failed to process {file_path}: {str(e)}")
            print(f"Error processing file {file_path}: {e}")

    def process_elements(self, elements, output_folder):
        all_elements_df = pd.DataFrame()
        try:
            for element in elements:
                # Collecting metadata for each element
                if element.metadata:
                    new_row = pd.DataFrame({
                        "Page Number": [element.metadata.page_number],
                        "Element ID": [element.id],
                        "Coordinates": [element.metadata.coordinates],
                        "Detection Class Probability": [element.metadata.detection_class_prob],
                        "Category": [element.category],
                        "Text": [element.text]
                    })
                    # Concatenate new row to the DataFrame
                    all_elements_df = pd.concat([all_elements_df, new_row], ignore_index=True)
                # Save the DataFrame of all elements to CSV if not empty
                if not all_elements_df.empty:
                    csv_path = output_folder / "elements_data.csv"
                    all_elements_df.to_csv(csv_path, index=False)
                # Process and save tables
                if element.category == "Table":
                    import openpyxl
                    self.save_table(element, output_folder)
        except Exception as e:
            logging.error(f"Error processing elements: {str(e)}")
            print(f"Error processing elements: {e}")
    def save_table(self, table_element, output_folder):
        html_content = table_element.metadata.text_as_html
        page_number = table_element.metadata.page_number
        table_index = table_element.id
        html_path = output_folder / f"table_{page_number}_{table_index}.html"
        csv_path = output_folder / f"table_{page_number}_{table_index}.csv"
        excel_path = output_folder / f"table_{page_number}_{table_index}.xlsx"
        try:
            tables = pd.read_html(io.StringIO(html_content))
            if tables:
                cell_df = table_element.metadata.table_as_cells
                temp_df = tables[0]  # Take the first table found
                temp_df["Page Number"] = page_number
                temp_df["Parent Element"] = table_element.metadata.parent_id
                temp_df.to_html(html_path, index=False)
                temp_df.to_csv(csv_path, index=False)
                cell_df.to_excel(excel_path, index=False)
            else:
                logging.info(f"No tables found on page {page_number}")
        except Exception as e:
            logging.error(f"Failed to save table from page {page_number}: {str(e)}")

if __name__ == "__main__":
    try:
        onedrive_path = get_onedrive_path() + r"\FDD Database\EFD\FDD Database"
        processor = PDFProcessor(onedrive_path)
        processor.process_pdfs()
    except Exception as e:
        logging.critical(f"An unexpected error stopped the processing: {e}")
