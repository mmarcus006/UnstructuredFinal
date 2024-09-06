import re
from pathlib import Path
import os

def extract_year_from_filename(filename: str) -> str:
    match = re.search(r'_(\d{4})_', filename)
    return match.group(1) if match else "0000"

def extract_entity_name(file_path: Path) -> str:
    # Extract entity name from the file name
    file_name = file_path.stem  # Get file name without extension
    # Match everything up to the year
    match = re.match(r'(.+?)_\d{4}_', file_name)
    if match:
        return match.group(1).replace('_', ' ')
    return "Unknown"

def get_original_output_folder(file_path: Path, base_output_dir: Path) -> Path:
    # Extract entity name from the file name (old method)
    file_name = file_path.stem
    parts = file_name.split('_')
    original_entity_name = parts[0] if parts else "Unknown"
    
    year = extract_year_from_filename(file_path.name)
    return base_output_dir / f"{original_entity_name}_{year}"

def get_output_folder(file_path: Path, base_output_dir: Path) -> Path:
    entity_name = extract_entity_name(file_path)
    year = extract_year_from_filename(file_path.name)
    return base_output_dir / f"{entity_name}_{year}"

def rename_output_folder_if_exists(file_path: Path, base_output_dir: Path) -> Path:
    original_folder = get_original_output_folder(file_path, base_output_dir)
    new_folder = get_new_output_folder(file_path, base_output_dir)
    
    if original_folder.exists():
        try:
            original_folder.rename(new_folder)
            print(f"Renamed folder from {original_folder} to {new_folder}")
        except OSError as e:
            print(f"Error renaming folder: {e}")
            return original_folder
    
    return new_folder

def is_already_processed(output_folder: Path) -> bool:
    return output_folder.exists() and (output_folder / "elements_data.csv").exists()

def copy_pdf_to_output(source_path: Path, destination_folder: Path):
    destination_path = destination_folder / source_path.name
    destination_path.write_bytes(source_path.read_bytes())