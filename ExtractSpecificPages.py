import os
import fitz  # PyMuPDF


def extract_pages_from_pdf(pdf_path, output_dir):
    """Extracts specific pages from the PDF and saves them as new PDF files."""
    doc = fitz.open(pdf_path)
    exhibit_page_num = None
    toc_page_num = None
    max_pages_to_extract = 6  # TOC page + 5 additional pages

    # Iterate through each page to find the required pages
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text()

        if exhibit_page_num is None and "How to Use This Franchise Disclosure Document" in text:
            exhibit_page_num = page_num

        if toc_page_num is None and "TABLE OF CONTENT" in text:
            toc_page_num = page_num
            break

    # Extract and save the 'How to Use This Franchise Disclosure Document' page if found
    if exhibit_page_num is not None:
        save_page_as_pdf(doc, exhibit_page_num, pdf_path, output_dir, "ExhibitPage")
    else:
        print(f"No 'How to Use This Franchise Disclosure Document' page found in {pdf_path}")

    # Extract and save the TOC page and up to 5 subsequent pages if found
    if toc_page_num is not None:
        extracted_pages = []
        for i in range(max_pages_to_extract):
            current_page_num = toc_page_num + i
            if current_page_num < len(doc):
                page = doc.load_page(current_page_num)
                extracted_pages.append(current_page_num)

                if "item 1" in page.get_text().lower():
                    break

        save_pages_as_pdf(doc, extracted_pages, pdf_path, output_dir, "TOC_and_Related")
    else:
        print(f"No 'TABLE OF CONTENT' page found in {pdf_path}")

def save_page_as_pdf(doc, page_num, original_pdf_path, output_dir, suffix):
    """Saves a specific page from the document as a new PDF file."""
    new_doc = fitz.open()  # Create a new PDF
    new_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)

    # Create a new file name
    original_filename = os.path.basename(original_pdf_path)
    base_filename, _ = os.path.splitext(original_filename)
    new_filename = f"{base_filename}_{suffix}.pdf"
    new_filename = "".join(c for c in new_filename if c not in '<>:"/\\|?*')  # Remove invalid characters

    new_filepath = os.path.join(output_dir, new_filename)

    # Check if file already exists
    if os.path.exists(new_filepath):
        print(f"File already exists: {new_filepath}. Skipping.")
        return

    new_doc.save(new_filepath)
    print(f"Saved: {new_filepath}")

def save_pages_as_pdf(doc, page_numbers, original_pdf_path, output_dir, suffix):
    """Saves specific pages from the document as a new PDF file."""
    new_doc = fitz.open()  # Create a new PDF
    for page_num in page_numbers:
        new_page = new_doc.new_page(width=doc[page_num].rect.width, height=doc[page_num].rect.height)
        new_page.show_pdf_page(new_page.rect, doc, page_num)

    # Create a new file name
    original_filename = os.path.basename(original_pdf_path)
    base_filename, _ = os.path.splitext(original_filename)
    new_filename = f"{base_filename}_{suffix}.pdf"
    new_filename = "".join(c for c in new_filename if c not in '<>:"/\\|?*')  # Remove invalid characters

    new_filepath = os.path.join(output_dir, new_filename)

    # Check if file already exists
    if os.path.exists(new_filepath):
        print(f"File already exists: {new_filepath}. Skipping.")
        return

    new_doc.save(new_filepath)
    print(f"Saved: {new_filepath}")

def process_pdfs_in_directory(directory):
    output_dir = os.path.join(directory, "extracted_pages")
    os.makedirs(output_dir, exist_ok=True)

    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(".pdf"):
                pdf_path = os.path.join(root, file)
                print(f"Processing: {pdf_path}")
                extract_pages_from_pdf(pdf_path, output_dir)

if __name__ == "__main__":
    directory_path = r"C:\Users\Miller\OneDrive\FDD Database\EFD\FDD Database"  # Replace with your directory path
    process_pdfs_in_directory(directory_path)
