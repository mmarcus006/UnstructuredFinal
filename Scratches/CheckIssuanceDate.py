import fitz  # PyMuPDF
import os
import pandas as pd
import re
from collections import defaultdict


# Function to extract text from a PDF and stop after finding "Issuance Date" or reaching 21st page
def extract_text_from_pdf(pdf_path):
    with fitz.open(pdf_path) as doc:
        text = ""
        issuance_date_line = None
        is_ocred = False
        for i, page in enumerate(doc):
            if i >= 21:
                break
            page_text = page.get_text()
            text += page_text
            if page_text.strip():
                is_ocred = True  # If there's any text, we assume the document is OCRed
            issuance_date_line = search_issuance_date(page_text)
            if issuance_date_line:
                break
    return text, issuance_date_line, is_ocred


# Function to search for the "Issuance Date" phrase
def search_issuance_date(text):
    lines = text.split('\n')
    for line in lines:
        if "Issuance Date" in line:
            return line
    return None


# Function to clean text for Excel compatibility
def clean_text(text):
    # Remove any non-printable characters
    return re.sub(r'[\x00-\x1F\x7F-\x9F]', '', text)


# Main folder path
base_folder = r"C:\Users\Miller\OneDrive\FDD Database\EFD\FDD Database"
log_file_path = os.path.join(base_folder, "unprocessed_pdfs.log")

# Data to store results
data = []
unprocessed_files = []
issuance_dates = defaultdict(list)

# Loop through all PDF files in the folder and subfolders
for root, dirs, files in os.walk(base_folder):
    # Skip processing if there's an Unstructured_YEAR folder
    subfolder_years = set(re.findall(r'Unstructured_(\d{4})', ' '.join(dirs)))
    for file in files:
        if file.lower().endswith(".pdf"):
            pdf_path = os.path.join(root, file)
            try:
                text, issuance_date_line, is_ocred = extract_text_from_pdf(pdf_path)
                if issuance_date_line:
                    # Get file size
                    file_size = os.path.getsize(pdf_path)

                    # Split the root to get base path and subfolders
                    base_path = base_folder
                    subfolders = os.path.relpath(root, base_folder).split(os.sep)
                    subfolder_year = next((year for year in subfolders if year.isdigit()), None)

                    # If there's an Unstructured_YEAR folder matching the subfolder year, skip deletion
                    if subfolder_year in subfolder_years:
                        continue

                    # Clean the issuance_date_line
                    issuance_date_line = clean_text(issuance_date_line)

                    # Store issuance date and file path
                    issuance_dates[root].append((issuance_date_line, pdf_path))

                    # Create a data row including the filename
                    row = [base_path] + subfolders + [file, issuance_date_line, is_ocred, file_size]
                    data.append(row)
            except Exception as e:
                # Log the path of the unprocessed file
                unprocessed_files.append(pdf_path)
                print(f"Failed to process {pdf_path}: {e}")

# Process issuance dates for deletion and logging
for subfolder, dates in issuance_dates.items():
    if len(dates) > 1:
        unique_dates = set(date for date, _ in dates)
        if len(unique_dates) == 1:
            # All issuance dates are the same, delete all but one PDF
            for i, (date, path) in enumerate(dates):
                if i > 0:
                    print("removed", path)
                    os.remove(path)
        else:
            # Issuance dates differ, log them
            for date, path in dates:
                row = [subfolder, date, path]
                data.append(row)
                print(row)
# Determine the maximum number of subfolder columns needed
max_subfolder_length = max(len(row) - 5 for row in data)  # Adjusted to accommodate the filename

# Create column names including 'Filename'
columns = ["Base Path"] + [f"Subfolder {i + 1}" for i in range(max_subfolder_length)] + ["Filename",
                                                                                         "Issuance Date Line",
                                                                                         "Is OCRed",
                                                                                         "File Size (bytes)",
                                                                                         "Subfolder",
                                                                                         "Differing Issuance Date",
                                                                                         "File Path"]

# Create a DataFrame
df = pd.DataFrame(data, columns=columns)

# Write the DataFrame to an Excel file
output_path = os.path.join(base_folder, "issuance_dates.xlsx")
df.to_excel(output_path, index=False)

# Write the unprocessed files to a log file
with open(log_file_path, 'w') as log_file:
    for unprocessed_file in unprocessed_files:
        log_file.write(f"{unprocessed_file}\n")

print(f"Data written to {output_path}")
print(f"Unprocessed PDF files logged to {log_file_path}")
