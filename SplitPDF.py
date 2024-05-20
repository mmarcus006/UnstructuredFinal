import os
import pandas as pd
import fitz  # PyMuPDF

# Define the file paths
excel_path = r"C:\Users\Miller\OneDrive\GetPageNumbersFromUnstructured.xlsm"
pdf_directory = r"C:\Users\Miller\OneDrive\FDD Database\EFD\Database By Sector\Coffee"

# Load the Excel workbook and sheet
print(f"Reading Excel file: {excel_path}")
df = pd.read_excel(excel_path, sheet_name='CleanedParsingData')

print("Excel file read successfully.")
print("First few rows of the dataframe:")
print(df.head())

# Mapping of file names to their correct paths based on the provided image
file_paths = {
    "Caribou Coffee_2014.pdf": r"C:\Users\Miller\OneDrive\FDD Database\EFD\Database By Sector\Coffee\Caribou Coffee\Caribou Coffee_2014.pdf",
    "Caribou Coffee_2015.pdf": r"C:\Users\Miller\OneDrive\FDD Database\EFD\Database By Sector\Coffee\Caribou Coffee\Caribou Coffee_2015.pdf",
    "Caribou Coffee_2016.pdf": r"C:\Users\Miller\OneDrive\FDD Database\EFD\Database By Sector\Coffee\Caribou Coffee\Caribou Coffee_2016.pdf",
    "Caribou Coffee_2017.pdf": r"C:\Users\Miller\OneDrive\FDD Database\EFD\Database By Sector\Coffee\Caribou Coffee\Caribou Coffee_2017.pdf",
    "Caribou Coffee_2018.pdf": r"C:\Users\Miller\OneDrive\FDD Database\EFD\Database By Sector\Coffee\Caribou Coffee\Caribou Coffee_2018.pdf",
    "Caribou Coffee_2019.pdf": r"C:\Users\Miller\OneDrive\FDD Database\EFD\Database By Sector\Coffee\Caribou Coffee\Caribou Coffee_2019.pdf",
    "Caribou Coffee_2020.pdf": r"C:\Users\Miller\OneDrive\FDD Database\EFD\Database By Sector\Coffee\Caribou Coffee\Caribou Coffee_2020.pdf",
    "Caribou Coffee_2021.pdf": r"C:\Users\Miller\OneDrive\FDD Database\EFD\Database By Sector\Coffee\Caribou Coffee\Caribou Coffee_2021.pdf",
    "Caribou Coffee_2022.pdf": r"C:\Users\Miller\OneDrive\FDD Database\EFD\Database By Sector\Coffee\Caribou Coffee\Caribou Coffee_2022.pdf",
    "Caribou Coffee_2023.pdf": r"C:\Users\Miller\OneDrive\FDD Database\EFD\Database By Sector\Coffee\Caribou Coffee\Caribou Coffee_2023.pdf",
    "Dunkin' Donuts_2008.pdf": r"C:\Users\Miller\OneDrive\FDD Database\EFD\Database By Sector\Coffee\Dunkin' FDDs\Dunkin' Donuts_2008.pdf",
    "Dunkin' Donuts_2010.pdf": r"C:\Users\Miller\OneDrive\FDD Database\EFD\Database By Sector\Coffee\Dunkin' FDDs\Dunkin' Donuts_2010.pdf",
    "Dunkin' Donuts_2011.pdf": r"C:\Users\Miller\OneDrive\FDD Database\EFD\Database By Sector\Coffee\Dunkin' FDDs\Dunkin' Donuts_2011.pdf",
    "Dunkin' Donuts_2013.pdf": r"C:\Users\Miller\OneDrive\FDD Database\EFD\Database By Sector\Coffee\Dunkin' FDDs\Dunkin' Donuts_2013.pdf",
    "Dunkin' Donuts_2014.pdf": r"C:\Users\Miller\OneDrive\FDD Database\EFD\Database By Sector\Coffee\Dunkin' FDDs\Dunkin' Donuts_2014.pdf",
    "Dunkin' Donuts_2015.pdf": r"C:\Users\Miller\OneDrive\FDD Database\EFD\Database By Sector\Coffee\Dunkin' FDDs\Dunkin' Donuts_2015.pdf",
    "Dunkin' Donuts_2016.pdf": r"C:\Users\Miller\OneDrive\FDD Database\EFD\Database By Sector\Coffee\Dunkin' FDDs\Dunkin' Donuts_2016.pdf",
    "Dunkin' Donuts_2017.pdf": r"C:\Users\Miller\OneDrive\FDD Database\EFD\Database By Sector\Coffee\Dunkin' FDDs\Dunkin' Donuts_2017.pdf",
    "Dunkin' Donuts_2018.pdf": r"C:\Users\Miller\OneDrive\FDD Database\EFD\Database By Sector\Coffee\Dunkin' FDDs\Dunkin' Donuts_2018.pdf",
    "Dunkin' Donuts_2019.pdf": r"C:\Users\Miller\OneDrive\FDD Database\EFD\Database By Sector\Coffee\Dunkin' FDDs\Dunkin' Donuts_2019.pdf",
    "Dunkin' Donuts_2020.pdf": r"C:\Users\Miller\OneDrive\FDD Database\EFD\Database By Sector\Coffee\Dunkin' FDDs\Dunkin' Donuts_2020.pdf",
    "Dunkin' Donuts_2021.pdf": r"C:\Users\Miller\OneDrive\FDD Database\EFD\Database By Sector\Coffee\Dunkin' FDDs\Dunkin' Donuts_2021.pdf",
    "Dunkin' Donuts_2022.pdf": r"C:\Users\Miller\OneDrive\FDD Database\EFD\Database By Sector\Coffee\Dunkin' FDDs\Dunkin' Donuts_2022.pdf",
    "Dunkin' Donuts_2023.pdf": r"C:\Users\Miller\OneDrive\FDD Database\EFD\Database By Sector\Coffee\Dunkin' FDDs\Dunkin' Donuts_2023.pdf",
    "Dutch Bros._2012.pdf": r"C:\Users\Miller\OneDrive\FDD Database\EFD\Database By Sector\Coffee\Dutch Bros\Dutch Bros._2012.pdf",
    "Dutch Bros._2013.pdf": r"C:\Users\Miller\OneDrive\FDD Database\EFD\Database By Sector\Coffee\Dutch Bros\Dutch Bros._2013.pdf",
    "Dutch Bros._2014.pdf": r"C:\Users\Miller\OneDrive\FDD Database\EFD\Database By Sector\Coffee\Dutch Bros\Dutch Bros._2014.pdf",
    "Dutch Bros._2015.pdf": r"C:\Users\Miller\OneDrive\FDD Database\EFD\Database By Sector\Coffee\Dutch Bros\Dutch Bros._2015.pdf",
    "Dutch Bros._2016.pdf": r"C:\Users\Miller\OneDrive\FDD Database\EFD\Database By Sector\Coffee\Dutch Bros\Dutch Bros._2016.pdf",
    "Dutch Bros._2017.pdf": r"C:\Users\Miller\OneDrive\FDD Database\EFD\Database By Sector\Coffee\Dutch Bros\Dutch Bros._2017.pdf",
    "Dutch Bros._2018.pdf": r"C:\Users\Miller\OneDrive\FDD Database\EFD\Database By Sector\Coffee\Dutch Bros\Dutch Bros._2018.pdf",
    "Scooter's Coffee_2011.pdf": r"C:\Users\Miller\OneDrive\FDD Database\EFD\Database By Sector\Coffee\Scooter's Coffee\Scooter's Coffee_2011.pdf",
    "Scooter's Coffee_2012.pdf": r"C:\Users\Miller\OneDrive\FDD Database\EFD\Database By Sector\Coffee\Scooter's Coffee\Scooter's Coffee_2012.pdf",
    "Scooter's Coffee_2013.pdf": r"C:\Users\Miller\OneDrive\FDD Database\EFD\Database By Sector\Coffee\Scooter's Coffee\Scooter's Coffee_2013.pdf",
    "Scooter's Coffee_2014.pdf": r"C:\Users\Miller\OneDrive\FDD Database\EFD\Database By Sector\Coffee\Scooter's Coffee\Scooter's Coffee_2014.pdf",
    "Scooter's Coffee_2015.pdf": r"C:\Users\Miller\OneDrive\FDD Database\EFD\Database By Sector\Coffee\Scooter's Coffee\Scooter's Coffee_2015.pdf",
    "Scooter's Coffee_2016.pdf": r"C:\Users\Miller\OneDrive\FDD Database\EFD\Database By Sector\Coffee\Scooter's Coffee\Scooter's Coffee_2016.pdf",
    "Scooter's Coffee_2017.pdf": r"C:\Users\Miller\OneDrive\FDD Database\EFD\Database By Sector\Coffee\Scooter's Coffee\Scooter's Coffee_2017.pdf",
    "Scooter's Coffee_2018.pdf": r"C:\Users\Miller\OneDrive\FDD Database\EFD\Database By Sector\Coffee\Scooter's Coffee\Scooter's Coffee_2018.pdf",
    "Scooter's Coffee_2019.pdf": r"C:\Users\Miller\OneDrive\FDD Database\EFD\Database By Sector\Coffee\Scooter's Coffee\Scooter's Coffee_2019.pdf",
    "Scooter's Coffee_2020.pdf": r"C:\Users\Miller\OneDrive\FDD Database\EFD\Database By Sector\Coffee\Scooter's Coffee\Scooter's Coffee_2020.pdf",
    "Scooter's Coffee_2021.pdf": r"C:\Users\Miller\OneDrive\FDD Database\EFD\Database By Sector\Coffee\Scooter's Coffee\Scooter's Coffee_2021.pdf",
    "Scooter's Coffee_2022.pdf": r"C:\Users\Miller\OneDrive\FDD Database\EFD\Database By Sector\Coffee\Scooter's Coffee\Scooter's Coffee_2022.pdf",
    "Scooter's Coffee_2023.pdf": r"C:\Users\Miller\OneDrive\FDD Database\EFD\Database By Sector\Coffee\Scooter's Coffee\Scooter's Coffee_2023.pdf",
    "Scooter's Coffee_2024.pdf": r"C:\Users\Miller\OneDrive\FDD Database\EFD\Database By Sector\Coffee\Scooter's Coffee\Scooter's Coffee_2024.pdf"
}

# Replace file paths in the dataframe
updated_paths = 0
for index, row in df.iterrows():
    pdf_name = os.path.basename(row['Column1']).strip()  # Get the file name from the path and strip whitespace
    if pdf_name in file_paths:
        df.at[index, 'Column1'] = file_paths[pdf_name]
        updated_paths += 1
        print(f"Updated path for {pdf_name}: {file_paths[pdf_name]}")

print(f"Updated paths in the dataframe: {updated_paths} paths updated.")
print(df.head())

# Create a dictionary to store page ranges and names for each PDF
page_ranges = {}
for index, row in df.iterrows():
    pdf_path = row['Column1']
    start_page = row['Start Page Number']
    end_page = row['End Page Number']
    element_id = row['Element ID']

    if pdf_path.lower().endswith('.pdf'):  # Ensure the file path is for a PDF
        if pdf_path not in page_ranges:
            page_ranges[pdf_path] = []
        page_ranges[pdf_path].append((start_page, end_page, element_id))
    else:
        print(f"Skipping non-PDF file: {pdf_path}")

# Check if any PDF files were found
if not page_ranges:
    print("No valid PDF files found in the Excel sheet.")
    exit(1)

# Traverse the directory tree and process PDFs
for root, _, files in os.walk(pdf_directory):
    for file in files:
        if file.lower().endswith('.pdf'):
            pdf_path = os.path.join(root, file)
            pdf_path = os.path.normpath(pdf_path)  # Normalize the path for consistency

            # Check if the current PDF path matches any in the page_ranges dictionary
            if pdf_path in page_ranges:
                print(f"Processing file: {pdf_path}")

                # Parse the year from the file path
                year = os.path.basename(pdf_path).split('_')[-1][:4]
                print(f"Year parsed: {year}")

                # Create a new folder for the year if it doesn't exist
                year_folder = os.path.join(pdf_directory, year)
                if not os.path.exists(year_folder):
                    os.makedirs(year_folder)
                    print(f"Created directory: {year_folder}")
                else:
                    print(f"Directory already exists: {year_folder}")

                # Attempt to read the PDF file
                try:
                    pdf_document = fitz.open(pdf_path)
                    print(f"Opened PDF: {pdf_path}")
                except Exception as e:
                    print(f"Error reading {pdf_path}: {e}")
                    continue

                for start_page, end_page, element_id in page_ranges[pdf_path]:
                    print(f"Processing pages: {start_page}-{end_page}, Element ID: {element_id}")

                    # Create a new PDF for the split pages
                    pdf_writer = fitz.open()

                    # Add the specified page range to the PDF writer
                    for page in range(start_page - 1, end_page):
                        pdf_writer.insert_pdf(pdf_document, from_page=page, to_page=page)

                    # Define the output PDF file path
                    pdf_name = os.path.basename(pdf_path)
                    output_pdf_path = os.path.join(year_folder,
                                                   f"{pdf_name[:-4]}_{start_page}-{end_page}_{element_id}.pdf")

                    # Save the split PDF to the new file
                    pdf_writer.save(output_pdf_path)
                    pdf_writer.close()

                    print(f"Created {output_pdf_path}")

                pdf_document.close()

print("PDF splitting completed.")
