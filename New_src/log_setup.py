import logging
from pathlib import Path

def setup_logging(output_dir: Path) -> logging.Logger:
    log_dir = output_dir / 'logs'
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / 'pdf_processing.log'
    
    logger = logging.getLogger('pdf_processor')
    logger.setLevel(logging.DEBUG)
    
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger
