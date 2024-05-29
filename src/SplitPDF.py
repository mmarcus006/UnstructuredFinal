import pandas as pd
import fitz  # PyMuPDF
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()


def create_output_dir(output_base_dir, entity, year):
    try:
        output_dir = os.path.join(output_base_dir, entity, year)
        os.makedirs(output_dir, exist_ok=True)
        return output_dir
    except Exception as e:
        logger.error(f"Error creating output directory for entity {entity} and year {year}: {e}")
        return None


def extract_entity_and_year(pdf_file):
    try:
        path_parts = pdf_file.split('\\')
        file_name = os.path.basename(pdf_file)
        entity = path_parts[-3]
        year = path_parts[-2] # Extracting year from the file name
        return entity, year
    except Exception as e:
        logger.error(f"Error extracting entity and year from {pdf_file}: {e}")
        return 'UnknownEntity', 'UnknownYear'


def split_pdf(row, output_base_dir):
    try:
        pdf_file = row['PDF File Path']
        start_page = row['Start Page Number']
        end_page = row['End Page Number']
        title = row['Text']

        # Extract entity and year from the file path
        entity, year = extract_entity_and_year(pdf_file)

        # Create the corresponding output directory structure
        output_dir = create_output_dir(output_base_dir, entity, year)
        if output_dir is None:
            return

        # Open the PDF file
        pdf_document = fitz.open(pdf_file)

        # Create a new PDF for the specified page range
        new_pdf = fitz.open()
        new_pdf.insert_pdf(pdf_document, from_page=start_page - 1, to_page=end_page - 1)

        # Save the new PDF with the specified title
        output_file_path = os.path.join(output_dir, f"{title}.pdf")
        new_pdf.save(output_file_path)
        new_pdf.close()
        pdf_document.close()

        logger.info(f"Successfully split PDF: {output_file_path}")
    except Exception as e:
        logger.error(f"Error processing PDF {pdf_file}: {e}")


def main():
    excel_path = r"C:\Users\Miller\OneDrive\GetPageNumbersFromUnstructured.xlsm"
    output_base_dir = r"C:\Users\Miller\OneDrive\Split_PDFs"

    # Load the Excel file
    sheet_name = 'CleanedParsingData_Python'
    df = pd.read_excel(excel_path, sheet_name=sheet_name)

    # Iterate through each row in the dataframe and process the PDFs
    for index, row in df.iterrows():
        split_pdf(row, output_base_dir)

    logger.info("PDF splitting completed successfully.")


if __name__ == "__main__":
    main()
