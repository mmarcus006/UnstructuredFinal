import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import json
from typing import List, Dict, Tuple, Any
import pandas as pd
from src.pdf_processor import PDFProcessor
from src.file_handler import save_elements_data, save_metadata_json, save_metadata_html, save_tables, load_error_files, update_error_log, generate_summary_report
from src.Config import load_config
from src.utils import extract_year_from_filename, extract_entity_name

class TestPDFProcessor(unittest.TestCase):
    def setUp(self):
        self.config = MagicMock()
        self.processor = PDFProcessor(self.config)

    @patch('New_src.pdf_processor.partition_pdf')
    def test_process_file(self, mock_partition_pdf):
        mock_partition_pdf.return_value = []
        file_path = Path('/test/file.pdf')
        result = self.processor._process_file(file_path)
        self.assertEqual(result, file_path)

class TestFileHandler(unittest.TestCase):
    def test_save_elements_data(self):
        df = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4]})
        output_folder = Path('/test/output')
        with patch('pandas.DataFrame.to_csv') as mock_to_csv:
            save_elements_data(df, output_folder)
            mock_to_csv.assert_called_once()

    def test_save_metadata_json(self):
        metadata = [{'key': 'value'}]
        output_folder = Path('/test/output')
        with patch('builtins.open', unittest.mock.mock_open()) as mock_file:
            save_metadata_json(metadata, output_folder)
            mock_file.assert_called_once()

    def test_load_error_files(self):
        error_log_file = Path('/test/error_log.json')
        with patch('builtins.open', unittest.mock.mock_open(read_data='["file1.pdf", "file2.pdf"]')):
            result = load_error_files(error_log_file)
            self.assertEqual(result, ["file1.pdf", "file2.pdf"])

class TestConfig(unittest.TestCase):
    @patch('builtins.open', unittest.mock.mock_open(read_data='input_dir: /input\noutput_dir: /output'))
    def test_load_config(self):
        config = load_config('config.yaml')
        self.assertEqual(config['input_dir'], Path('/input'))
        self.assertEqual(config['output_dir'], Path('/output'))

class TestUtils(unittest.TestCase):
    def test_extract_year_from_filename(self):
        filename = 'document_2023_test.pdf'
        year = extract_year_from_filename(filename)
        self.assertEqual(year, '2023')

    def test_extract_entity_name(self):
        file_path = Path('/Company/Documents/EntityName/2023/file.pdf')
        entity_name = extract_entity_name(file_path)
        self.assertEqual(entity_name, 'EntityName')

if __name__ == '__main__':
    unittest.main()
