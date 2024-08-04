import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock
from New_src.pdf_processor import PDFProcessor, PDFProcessingError


class TestPDFProcessor(unittest.TestCase):

    def setUp(self):
        self.config = {
            'input_dir': 'samples',
            'output_dir': 'output',
            'num_workers': 2,
            'retry_attempts': 2
        }
        self.processor = PDFProcessor(self.config)

    @patch('New_src.pdf_processor.ProcessPoolExecutor')
    @patch('New_src.pdf_processor.tqdm')
    @patch('New_src.pdf_processor.generate_summary_report')
    def test_process_pdfs(self, mock_generate_summary_report, mock_tqdm, mock_executor):
        mock_executor_instance = mock_executor.return_value.__enter__.return_value
        mock_future = MagicMock()
        mock_future.result.return_value = True
        mock_executor_instance.submit.return_value = mock_future

        self.processor.process_pdfs()

        mock_executor.assert_called_once_with(max_workers=self.config['num_workers'])
        mock_generate_summary_report.assert_called_once()

    @patch('New_src.pdf_processor.partition_pdf')
    @patch('New_src.pdf_processor.process_elements')
    @patch('New_src.pdf_processor.save_elements_data')
    @patch('New_src.pdf_processor.save_metadata_json')
    @patch('New_src.pdf_processor.save_metadata_html')
    @patch('New_src.pdf_processor.save_tables')
    @patch('New_src.pdf_processor.copy_pdf_to_output')
    def test_process_file(self, mock_copy_pdf_to_output, mock_save_tables, mock_save_metadata_html,
                          mock_save_metadata_json,
                          mock_save_elements_data, mock_process_elements, mock_partition_pdf):
        file_path = Path('samples/sample.pdf')
        mock_partition_pdf.return_value = []
        mock_process_elements.return_value = ([], [], [])

        self.processor._process_file(file_path)

        mock_partition_pdf.assert_called_once()
        mock_process_elements.assert_called_once()
        mock_save_elements_data.assert_called_once()
        mock_save_metadata_json.assert_called_once()
        mock_save_metadata_html.assert_called_once()
        mock_save_tables.assert_called_once()
        mock_copy_pdf_to_output.assert_called_once()

    @patch.object(PDFProcessor, '_process_file')
    def test_process_file_with_retry(self, mock_process_file):
        file_path = Path('samples/sample.pdf')
        mock_process_file.side_effect = [PDFProcessingError("Error", str(file_path)), True]

        result = self.processor._process_file_with_retry(file_path)

        self.assertTrue(result)
        self.assertEqual(mock_process_file.call_count, 2)

    @patch.object(PDFProcessor, '_process_file')
    def test_process_file_with_retry_failure(self, mock_process_file):
        file_path = Path('samples/sample.pdf')
        mock_process_file.side_effect = PDFProcessingError("Error", str(file_path))

        result = self.processor._process_file_with_retry(file_path)

        self.assertFalse(result)
        self.assertEqual(mock_process_file.call_count, self.config['retry_attempts'])


if __name__ == '__main__':
    unittest.main()