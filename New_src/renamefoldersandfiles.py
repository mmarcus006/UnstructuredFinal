import csv
import re
import shutil
from pathlib import Path
from Config import load_config
from fuzzywuzzy import process
from tqdm import tqdm

def count_pdfs_in_subfolders():
    # Load the configuration
    config = load_config(r'C:\Users\Miller\PycharmProjects\UnstructuredFinal\New_src\config.yaml')
    output_dir = Path(config['output_dir'])
    
    # Define the folder containing the PDFs to match against
    match_folder = Path(r'C:\Users\Miller\OneDrive - franchiseportal.io\WISCONSINFDDs')
    
    # Get all PDF files in the match folder
    match_pdfs = list(match_folder.glob('*.pdf'))
    match_pdf_names = [pdf.stem for pdf in match_pdfs]

    # Prepare data for CSV
    pdf_data = []

    # Get the list of subfolders
    subfolders = [subfolder for subfolder in output_dir.iterdir() if subfolder.is_dir()]

    # Group subfolders by entity name
    entity_groups = {}
    for subfolder in subfolders:
        entity_name = re.sub(r'_\d{4}$', '', subfolder.name)
        if entity_name not in entity_groups:
            entity_groups[entity_name] = []
        entity_groups[entity_name].append(subfolder)

    # Create a progress bar
    with tqdm(total=len(subfolders), desc="Processing subfolders") as pbar:
        # Process each entity group
        for entity_name, folders in entity_groups.items():
            if len(folders) > 1:
                # Sort folders by name (which will put the one with year at the end)
                folders.sort(key=lambda x: x.name)
                # Keep the last folder (with year) and delete others
                for folder_to_delete in folders[:-1]:
                    shutil.rmtree(folder_to_delete)
                    print(f"Deleted duplicate folder: {folder_to_delete}")
                    pbar.update(1)
                folder_to_process = folders[-1]
            else:
                folder_to_process = folders[0]

            # Delete folder if it contains multiple PDFs
            if delete_folders_with_multiple_pdfs(folder_to_process):
                pbar.update(1)
                continue

            # Process the remaining folder
            pdf_files = list(folder_to_process.glob('*.pdf'))
            pdf_count = len(pdf_files)
            
            for pdf_file in pdf_files:
                # Perform fuzzy matching
                best_match, score = process.extractOne(pdf_file.stem, match_pdf_names)
                best_match_path = next(pdf for pdf in match_pdfs if pdf.stem == best_match)
                
                pdf_data.append([folder_to_process.name, pdf_count, str(pdf_file), str(best_match_path), score])
            
            pbar.update(1)

    # Save data to CSV
    csv_path = output_dir / 'pdf_inventory.csv'
    with csv_path.open('w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['Subfolder', 'PDF Count', 'PDF Path', 'Matched PDF Path', 'Match Score'])
        csv_writer.writerows(pdf_data)

    print(f"PDF inventory saved to {csv_path}")

if __name__ == "__main__":
    count_pdfs_in_subfolders()
