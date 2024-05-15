import fitz  # PyMuPDF

def test_pymupdf():
    try:
        doc = fitz.open()
        print("PyMuPDF is working correctly.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_pymupdf()
