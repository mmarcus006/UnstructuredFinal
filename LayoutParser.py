import layoutparser as lp
import cv2
from pdf2image import convert_from_path
import pytesseract
import pandas as pd
import logging

# Set up logging
logging.basicConfig(filename='document_processing.log', level=logging.INFO, format='%(asctime)s %(message)s')

# Function to convert PDF to images
def convert_pdf_to_images(pdf_path):
    try:
        pages = convert_from_path(pdf_path)
        logging.info(f"Converted PDF to images: {len(pages)} pages")
        print(f"Converted PDF to images: {len(pages)} pages")
        return pages
    except Exception as e:
        logging.error(f"Error converting PDF to images: {e}")
        raise

# Function to initialize the layout detection model
def initialize_layout_model():
    try:
        model = lp.Detectron2LayoutModel(config_path='lp://PubLayNet/faster_rcnn_R_50_FPN_3x/config',
                                         extra_config=["MODEL.ROI_HEADS.SCORE_THRESH_TEST", 0.5])
        logging.info("Initialized layout detection model")
        print("Initialized layout detection model")
        return model
    except Exception as e:
        logging.error(f"Error initializing layout model: {e}")
        raise

# Function to detect layouts on a single image
def detect_layout(image, model):
    try:
        layout = model.detect(image)
        tables = lp.Layout([b for b in layout if b.type == 'Table'])
        logging.info(f"Detected {len(tables)} tables in the image")
        print(f"Detected {len(tables)} tables in the image")
        return tables
    except Exception as e:
        logging.error(f"Error detecting layout: {e}")
        raise

# Function to perform OCR on table images using Tesseract
def ocr_table(table_image):
    try:
        text = pytesseract.image_to_string(table_image)
        logging.info("Performed OCR on table image")
        return text
    except Exception as e:
        logging.error(f"Error performing OCR: {e}")
        raise

# Function to process a single page and extract tables
def process_page(page_image, model):
    try:
        image = cv2.cvtColor(page_image, cv2.COLOR_RGB2BGR)
        tables = detect_layout(image, model)
        extracted_tables = []
        for table in tables:
            table_image = table.crop_image(image)
            text = ocr_table(table_image)
            extracted_tables.append(text)
        logging.info(f"Processed page and extracted {len(extracted_tables)} tables")
        print(f"Processed page and extracted {len(extracted_tables)} tables")
        return extracted_tables
    except Exception as e:
        logging.error(f"Error processing page: {e}")
        raise

# Function to save tables to CSV
def save_tables_to_csv(tables, output_path):
    try:
        df = pd.DataFrame(tables, columns=['Table Content'])
        df.to_csv(output_path, index=False)
        logging.info(f"Saved extracted tables to {output_path}")
        print(f"Saved extracted tables to {output_path}")
    except Exception as e:
        logging.error(f"Error saving tables to CSV: {e}")
        raise

# Function to process the entire document
def process_document(pdf_path, output_csv):
    try:
        pages = convert_pdf_to_images(pdf_path)
        model = initialize_layout_model()
        all_tables = []
        for page_number, page in enumerate(pages, start=1):
            tables = process_page(page, model)
            for table in tables:
                all_tables.append({'Page': page_number, 'Content': table})
        save_tables_to_csv(all_tables, output_csv)
        logging.info("Completed processing document")
        print("Completed processing document")
    except Exception as e:
        logging.error(f"Error processing document: {e}")
        raise

# Example Usage
if __name__ == "__main__":
    pdf_path = 'SamplePages.pdf'
    output_csv = 'extracted_tables.csv'
    process_document(pdf_path, output_csv)
