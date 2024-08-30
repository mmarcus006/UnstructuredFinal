import os
from pdf_processor import PDFProcessor
from Config import load_config
from log_setup import setup_logging
from pathlib import Path
import multiprocessing

def main():
    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Construct the path to config.yaml
    config_path = os.path.join(current_dir, 'config.yaml')
    
    config = load_config(config_path)
    logger = setup_logging(config['output_dir'])
    
    # Set the number of workers based on available CPU cores
    config['num_workers'] = min(config['num_workers'], multiprocessing.cpu_count() - 4)
    
    logger.info(f"Parallel processing: {'enabled' if config['parallel_processing'] else 'disabled'}")
    logger.info(f"Number of workers: {config['num_workers']}")

    try:
        processor = PDFProcessor(config)
        processor.process_pdfs()
        logger.info("PDF processing completed successfully")
    except Exception as e:
        logger.critical(f"An unexpected error occurred: {e}", exc_info=True)

if __name__ == "__main__":
    main()