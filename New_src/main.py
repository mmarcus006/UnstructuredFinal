# from pdf_processor import PDFProcessor
# from Config import load_config
# from log_setup import setup_logging
# from pathlib import Path
#
# def main():
#     config = load_config('config.yaml')
#     logger = setup_logging(config['output_dir'])
#     sample_pdf_path = Path(r"C:\Users\Miller\PycharmProjects\UnstructuredFinal\New_src\samples\sample.pdf")
#
#     try:
#         processor = PDFProcessor(config)
#         processor.process_pdfs() #uncomment to run the normal script on all pdf files
#         #processor.process_single_file(sample_pdf_path) #comment out to run the normal script on all pdf files
#         logger.info(f"Successfully processed sample PDF: {sample_pdf_path}")
#     except Exception as e:
#         logger.critical(f"An unexpected error occurred: {e}", exc_info=True)
#
# if __name__ == "__main__":
#     main()

from distributed_processor import DistributedProcessor
import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py [master|worker] [master_address]")
        sys.exit(1)

    is_master = sys.argv[1].lower() == 'master'
    master_address = sys.argv[2] if len(sys.argv) > 2 else 'localhost'

    processor = DistributedProcessor(is_master, master_address)
    processor.run()

if __name__ == "__main__":
    main()