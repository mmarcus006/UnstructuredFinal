import os
import fitz  # PyMuPDF
import requests
import json

# Define the API endpoint and model
API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3:8b-instruct-q8_0"

def extract_table_of_contents(pdf_path):
    """Extracts the text from the page containing 'Table Of Contents' and the following page."""
    doc = fitz.open(pdf_path)
    toc_text = ""
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text()
        if "TABLE OF CONTENT" in text:
            toc_text += text
            if page_num + 1 < len(doc):
                next_page = doc.load_page(page_num + 1)
                toc_text += next_page.get_text()
            break
    return toc_text

def send_to_llm(text):
    headers = {
        "Content-Type": "application/json"
    }
    prompt = f'Extract the table of contents from the following text: """{text}"""'
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": True
    }

    response = requests.post(API_URL, headers=headers, data=json.dumps(payload))

    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

    return response.json()

def process_pdfs_in_directory(directory):
    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(".pdf"):
                pdf_path = os.path.join(root, file)
                print(f"Processing: {pdf_path}")
                pdf_text = extract_table_of_contents(pdf_path)
                if pdf_text:
                    result = send_to_llm(pdf_text)
                    if result:
                        print(result)
                else:
                    print("No Table Of Contents found in the PDF.")

if __name__ == "__main__":
    directory_path = r"C:\Users\Miller\OneDrive\FDD Database\EFD\Database By Sector\Coffee"  # Replace with your directory path
    process_pdfs_in_directory(directory_path)
