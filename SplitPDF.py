import os
import pandas as pd
from PyPDF2 import PdfReader, PdfWriter

def split_pdf(pdf_path, table_path, output_dir_name):
    # Determine the output directory based on the PDF path and create it if necessary
    base_dir = os.path.dirname(pdf_path)
    output_dir = os.path.join(base_dir, output_dir_name)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Load the table with page numbers and titles
    df = pd.read_excel(table_path, sheet_name='Sheet1')
    # Ensure the dataframe is sorted by PageNumber just in case
    df.sort_values('PageNumber', inplace=True)

    # Open the PDF
    reader = PdfReader(pdf_path)

    # Prepare to iterate over each row in the DataFrame
    start_pages = df['PageNumber'].tolist()
    titles = df['Item'].tolist()
    # Convert start pages from 1-indexed to 0-indexed
    start_pages = [page - 1 for page in start_pages]
    start_pages.append(len(reader.pages))  # Append the total number of pages for the last segment

    # Iterate over each segment
    for i in range(len(start_pages) - 1):
        start_page = start_pages[i]
        end_page = start_pages[i + 1]
        title = titles[i].replace('/', '_').replace('â€™', "'")  # Clean up the title for file naming

        # Create a PDF writer object for the new PDF
        writer = PdfWriter()

        # Add pages for this segment
        for page in range(start_page, end_page):
            writer.add_page(reader.pages[page])

        # Save the new PDF
        output_pdf_path = os.path.join(output_dir, f"{title}.pdf")
        with open(output_pdf_path, 'wb') as f:
            writer.write(f)

# Example usage
pdf_path = r"C:\Users\Miller\OneDrive\FDD Database\EFD\Database By Sector\1-800-RADIATOR  AC\2023\1-800-RADIATOR  AC_2023_Virginia_509887.pdf"
table_path = r"C:\Users\Miller\OneDrive\FDD Database\EFD\Database By Sector\1-800-RADIATOR  AC\2023\Unstructured_Outputs\elements_data_edited.xlsx"
split_pdf(pdf_path, table_path, "PDF Pages")
