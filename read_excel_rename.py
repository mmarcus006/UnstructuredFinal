import csv
import os
import json
import shutil

def read_csv(file_path):
    with open(file_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        return list(reader)

def write_not_found_csv(not_found_files):
    with open('filesnotfound.csv', 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['File Type', 'Original Name', 'New Name', 'Error']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for file in not_found_files:
            writer.writerow(file)

def rename_files(data, base_folder, subfolder_base, items_folder):
    not_found_files = []

    for row in data:
        original_pdf = row['Original PDF File Name']
        new_pdf = row['New PDF File Name']
        subfolder_old = row['Subfolder Old Name']
        subfolder_new = row['New Subfolder Name']
        new_item_pdf = row['New Item PDF File Name']
        original_item_pdf = row['\ufeffName']  # This is the original item PDF name
        
        # Rename PDF file in base folder
        old_pdf_path = os.path.join(base_folder, original_pdf)
        new_pdf_path = os.path.join(base_folder, new_pdf)
        try:
            if os.path.exists(old_pdf_path):
                os.rename(old_pdf_path, new_pdf_path)
                print(f"Renamed: {original_pdf} -> {new_pdf}")
            else:
                print(f"File not found: {original_pdf}")
                not_found_files.append({'File Type': 'Main PDF', 'Original Name': original_pdf, 'New Name': new_pdf, 'Error': 'File not found'})
        except Exception as e:
            print(f"Error renaming {original_pdf}: {str(e)}")
            not_found_files.append({'File Type': 'Main PDF', 'Original Name': original_pdf, 'New Name': new_pdf, 'Error': str(e)})
        
        # Rename JSON file in base folder
        json_name = os.path.splitext(original_pdf)[0] + '_FranchiseInfo.json'
        new_json_name = os.path.splitext(new_pdf)[0] + '_FranchiseInfo.json'
        old_json_path = os.path.join(base_folder, json_name)
        new_json_path = os.path.join(base_folder, new_json_name)
        try:
            if os.path.exists(old_json_path):
                os.rename(old_json_path, new_json_path)
                print(f"Renamed: {json_name} -> {new_json_name}")
            else:
                print(f"File not found: {json_name}")
                not_found_files.append({'File Type': 'JSON', 'Original Name': json_name, 'New Name': new_json_name, 'Error': 'File not found'})
        except Exception as e:
            print(f"Error renaming {json_name}: {str(e)}")
            not_found_files.append({'File Type': 'JSON', 'Original Name': json_name, 'New Name': new_json_name, 'Error': str(e)})
        
        # Handle subfolder renaming or creation, and PDF renaming within subfolder
        if subfolder_old != '0':
            old_subfolder_path = os.path.join(subfolder_base, subfolder_old)
            new_subfolder_path = os.path.join(subfolder_base, subfolder_new)
            
            try:
                if os.path.exists(old_subfolder_path):
                    # Rename subfolder
                    os.rename(old_subfolder_path, new_subfolder_path)
                    print(f"Renamed subfolder: {subfolder_old} -> {subfolder_new}")
                else:
                    # Create new subfolder
                    os.makedirs(new_subfolder_path, exist_ok=True)
                    print(f"Created new subfolder: {subfolder_new}")
                
                # Find and rename PDF file within the subfolder
                old_item_pdf_path = os.path.join(new_subfolder_path, original_item_pdf)
                new_item_pdf_path = os.path.join(new_subfolder_path, new_item_pdf)
                if os.path.exists(old_item_pdf_path):
                    os.rename(old_item_pdf_path, new_item_pdf_path)
                    print(f"Renamed PDF in subfolder: {original_item_pdf} -> {new_item_pdf}")
                else:
                    print(f"File not found in subfolder: {original_item_pdf}")
                    not_found_files.append({'File Type': 'Subfolder PDF', 'Original Name': original_item_pdf, 'New Name': new_item_pdf, 'Error': 'File not found in subfolder'})
            except Exception as e:
                print(f"Error processing subfolder {subfolder_old}: {str(e)}")
                not_found_files.append({'File Type': 'Subfolder', 'Original Name': subfolder_old, 'New Name': subfolder_new, 'Error': str(e)})
        
        # Rename PDF in Items folder
        old_items_pdf_path = os.path.join(items_folder, original_item_pdf)
        new_items_pdf_path = os.path.join(items_folder, new_item_pdf)
        try:
            if os.path.exists(old_items_pdf_path):
                os.rename(old_items_pdf_path, new_items_pdf_path)
                print(f"Renamed PDF in Items folder: {original_item_pdf} -> {new_item_pdf}")
            else:
                print(f"File not found in Items folder: {original_item_pdf}")
                not_found_files.append({'File Type': 'Items PDF', 'Original Name': original_item_pdf, 'New Name': new_item_pdf, 'Error': 'File not found in Items folder'})
        except Exception as e:
            print(f"Error renaming file in Items folder {original_item_pdf}: {str(e)}")
            not_found_files.append({'File Type': 'Items PDF', 'Original Name': original_item_pdf, 'New Name': new_item_pdf, 'Error': str(e)})

    return not_found_files

def main():
    csv_path = 'RenamingTable.csv'  # Update this path if necessary
    base_folder = r'C:\Users\Miller\OneDrive - franchiseportal.io\WISCONSINFDDs'
    subfolder_base = r'C:\Users\Miller\OneDrive - franchiseportal.io\WisconsinFDD_Unstructured'
    items_folder = r'C:\Users\Miller\OneDrive - franchiseportal.io\WISCONSINFDDs\Items'
    
    try:
        data = read_csv(csv_path)
        not_found_files = rename_files(data, base_folder, subfolder_base, items_folder)
        write_not_found_csv(not_found_files)
        print(f"Files not found or renamed have been written to filesnotfound.csv")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
