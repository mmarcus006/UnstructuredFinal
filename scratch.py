import re

def delete_error_lines(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    lines = [line for line in lines if not re.search(r'ERROR:root:Failed to save table from page', line)]

    with open(file_path, 'w') as file:
        file.writelines(lines)

def extract_unique_filenames(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    file_paths = {re.search(r'Failed to process (.*): Error', line).group(1) for line in lines if re.search(r'Failed to process (.*): Error', line)}

    return file_paths

log_file_path = 'processing_errors.log'
delete_error_lines(log_file_path)
#unique_filenames = extract_unique_filenames(log_file_path)
#print(unique_filenames)
