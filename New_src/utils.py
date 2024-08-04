import re
from pathlib import Path

def extract_year_from_filename(filename: str) -> str:
    match = re.search(r'_(\d{4})_', filename)
    return match.group(1) if match else "0000"

def extract_entity_name(file_path: Path) -> str:
    # Extract entity name from the file name
    file_name = file_path.stem  # Get file name without extension
    # Assume the entity name is everything before the first underscore
    parts = file_name.split('_')
    return parts[0] if parts else "Unknown"

def get_output_folder(file_path: Path, base_output_dir: Path) -> Path:
    entity_name = extract_entity_name(file_path)
    year = extract_year_from_filename(file_path.name)
    return base_output_dir / f"{entity_name}_{year}"

def is_already_processed(output_folder: Path) -> bool:
    return output_folder.exists() and (output_folder / "elements_data.csv").exists()

def copy_pdf_to_output(source_path: Path, destination_folder: Path):
    destination_path = destination_folder / source_path.name
    destination_path.write_bytes(source_path.read_bytes())