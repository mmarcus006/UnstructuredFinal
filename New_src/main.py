from pdf_processor import PDFProcessor
from Config import load_config
from log_setup import setup_logging

def main():
    config = load_config('config.yaml')
    logger = setup_logging(config['output_dir'])

    try:
        processor = PDFProcessor(config)
        processor.process_pdfs()
    except Exception as e:
        logger.critical(f"An unexpected error occurred: {e}", exc_info=True)

if __name__ == "__main__":
    main()
