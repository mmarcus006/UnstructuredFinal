import os
import re
import pandas as pd
import PyPDF2
import spacy

# Initialize Spacy model for Named Entity Recognition
nlp = spacy.load("en_core_web_sm")
# Function to extract text from the first 10 pages of a PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        num_pages = min(10, len(reader.pages))
        for page_num in range(num_pages):
            text += reader.pages[page_num].extract_text()
    return text


# Function to extract date following the word "issuance"
def extract_issuance_date(text):
    doc = nlp(text)
    issuance_idx = text.lower().find("issuance")
    if issuance_idx == -1:
        return "No date"
    issuance_text = text[issuance_idx:issuance_idx + 100]  # Extract surrounding text
    doc = nlp(issuance_text)
    for ent in doc.ents:
        if ent.label_ == "DATE":
            return ent.text
    return "No date"


# Function to process a single file and return extracted data
def process_file(file_path):
    try:
        print(f"Processing file: {file_path}")
        text = extract_text_from_pdf(file_path)
        issuance_date = extract_issuance_date(text)
        print(f"Extracted issuance date: {issuance_date} from file: {file_path}")

        # Extract entity name and year from file path
        path_parts = file_path.split(os.sep)
        entity_name = path_parts[-3]
        year = path_parts[-2]

        return {
            "Full File Path": file_path,
            "Entity Name": entity_name,
            "Year": year,
            "Issuance Date": issuance_date
        }
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")
        return None


# Main function to loop through all PDFs in the specified folder
def process_pdfs_in_folder(base_folder):
    data = []
    for root, _, files in os.walk(base_folder):
        for file in files:
            if file.lower().endswith(".pdf"):
                file_path = os.path.join(root, file)
                file_data = process_file(file_path)
                if file_data is not None:
                    data.append(file_data)

    # Create DataFrame
    df = pd.DataFrame(data, columns=["Full File Path", "Entity Name", "Year", "Issuance Date"])
    return df


# Specify the base folder path
base_folder = r"C:\Users\Miller\OneDrive\FDD Database\EFD\FDD Database"

# Process PDFs and get the DataFrame
df = process_pdfs_in_folder(base_folder)

# Save the DataFrame to a CSV file
output_csv_path = os.path.join(base_folder, "extracted_issuance_dates.csv")
df.to_csv(output_csv_path, index=False)

print("Extraction complete. Data saved to:", output_csv_path)
