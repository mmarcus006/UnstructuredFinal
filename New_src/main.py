import sys
from pathlib import Path
from pdf_processor import PDFProcessor
from Config import load_config
from log_setup import setup_logging
import multiprocessing
from pillow_heif import register_heif_opener
import cv2
import unstructured_pytesseract

def main():
    try:
        # Get the directory of the current script using Path
        current_dir = Path(__file__).resolve().parent
        # Construct the path to config.yaml
        config_path = current_dir / 'config.yaml'

        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        config = load_config(str(config_path))
        logger = setup_logging(config['output_dir'])

        # Set the number of workers based on available CPU cores
        config['num_workers'] = min(config['num_workers'], multiprocessing.cpu_count() - 1)

        logger.info(f"Configuration loaded from: {config_path}")
        logger.info(f"Input directory: {config['input_dir']}")
        logger.info(f"Output directory: {config['output_dir']}")
        logger.info(f"Parallel processing: {'enabled' if config['parallel_processing'] else 'disabled'}")
        logger.info(f"Number of workers: {config['num_workers']}")
        logger.info(f"Batch size: {config['batch_size']}")

        # Validate input and output directories
        if not config['input_dir'].exists():
            raise FileNotFoundError(f"Input directory does not exist: {config['input_dir']}")

        config['output_dir'].mkdir(parents=True, exist_ok=True)

        processor = PDFProcessor(config)
        processor.process_pdfs()
        logger.info("PDF processing completed successfully")

    except FileNotFoundError as e:
        logger.critical(f"File not found: {e}")
        sys.exit(1)
    except KeyError as e:
        logger.critical(f"Missing configuration key: {e}")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"An unexpected error occurred: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()