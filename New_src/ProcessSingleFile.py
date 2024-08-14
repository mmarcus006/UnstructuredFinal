from unstructured.partition.pdf import partition_pdf
from pathlib import Path
import unstructured
import unstructured_inference


def test_partition_pdf(file_path):
    try:
        elements = partition_pdf(
            filename=str(file_path),
            strategy='hi_res',
            hi_res_model_name="yolox",
            infer_table_structure=True,
            include_metadata=True,
            include_page_breaks=True,
            extract_images_in_pdf=False,
            ocr_languages=['eng'],
            url=None
        )
        print(f"Successfully partitioned {file_path}")
        print(f"Number of elements: {len(elements)}")
    except Exception as e:
        print(f"Failed to partition {file_path}: {str(e)}")


# Usage
test_partition_pdf(r"C:\Users\Miller\PycharmProjects\UnstructuredFinal\New_src\samples\sample.pdf")
