import unittest
from pathlib import Path
from unstructured.partition.pdf import partition_pdf
from New_src.element_processor import extract_element_metadata, process_elements


class TestElementProcessor(unittest.TestCase):
    def setUp(self):
        sample_pdf_path = Path('C:/Users/Miller/PycharmProjects/UnstructuredFinal/New_src/samples/sample.pdf')
        self.elements = partition_pdf(filename=str(sample_pdf_path))

    def test_extract_element_metadata(self):
        for element in self.elements:
            metadata = extract_element_metadata(element)
            self.assertIsInstance(metadata, dict)
            self.assertIn('id', metadata)
            self.assertIn('text', metadata)
            self.assertIn('category', metadata)
            self.assertIn('coordinates', metadata)
            self.assertIn('detection_class_prob', metadata)

    def test_process_elements(self):
        all_elements_df, tables, all_elements_metadata = process_elements(self.elements)

        self.assertIsNotNone(all_elements_df)
        self.assertGreater(len(all_elements_df), 0)
        self.assertIsInstance(tables, list)
        self.assertIsInstance(all_elements_metadata, list)
        self.assertEqual(len(all_elements_metadata), len(self.elements))

        expected_columns = ['Page Number', 'Element ID', 'Coordinates', 'Detection Class Probability', 'Category',
                            'Text', 'Text as HTML']
        for column in expected_columns:
            self.assertIn(column, all_elements_df.columns)


if __name__ == '__main__':
    unittest.main()
