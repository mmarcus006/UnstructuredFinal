import json
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any

def save_elements_data(df: pd.DataFrame, output_folder: Path):
    csv_path = output_folder / "elements_data.csv"
    df.to_csv(csv_path, index=False)

def save_metadata_json(metadata: List[Dict[str, Any]], output_folder: Path):
    json_path = output_folder / "all_elements_metadata.json"
    with open(json_path, 'w') as f:
        json.dump(metadata, f, indent=2)

def save_metadata_html(metadata: List[Dict[str, Any]], output_folder: Path):
    html_path = output_folder / "all_elements_metadata.html"
    html_content = "<html><body><h1>Elements Metadata</h1>"
    for i, elem in enumerate(metadata, 1):
        html_content += f"<h2>Element {i}</h2>"
        html_content += "<table border='1'>"
        for key, value in elem.items():
            if isinstance(value, dict):
                html_content += f"<tr><th>{html.escape(str(key))}</th><td>"
                html_content += "<table border='1'>"
                for sub_key, sub_value in value.items():
                    html_content += f"<tr><th>{html.escape(str(sub_key))}</th><td>{html.escape(str(sub_value))}</td></tr>"
                html_content += "</table></td></tr>"
            else:
                html_content += f"<tr><th>{html.escape(str(key))}</th><td>{html.escape(str(value))}</td></tr>"
        html_content += "</table>"
    html_content += "</body></html>"

    with open(html_path, 'w') as f:
        f.write(html_content)

def save_tables(tables: List[Any], output_folder: Path):
    for table in tables:
        table_data = table.metadata.text_as_html
        page_number = table.metadata.page_number
        table_index = table.id

        tables_df = pd.read_html(table_data)
        if tables_df:
            cell_df = table.metadata.table_as_cells
            temp_df = tables_df[0]
            temp_df["Page Number"] = page_number
            temp_df["Parent Element"] = table.metadata.parent_id

            csv_path = output_folder / f"table_{page_number}_{table_index}.csv"
            temp_df.to_csv(csv_path, index=False)

            excel_path = output_folder / f"table_{page_number}_{table_index}.xlsx"
            temp_df.to_excel(excel_path, index=False)

            cell_csv_path = output_folder / f"table_cells_{page_number}_{table_index}.csv"
            cell_df.to_csv(cell_csv_path, index=True)

def load_error_files(error_log_file: Path) -> List[str]:
    if error_log_file.exists():
        try:
            with open(error_log_file, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []

def update_error_log(error_files: List[str], error_log_file: Path):
    with open(error_log_file, 'w') as f:
        json.dump(error_files, f, indent=2)

def generate_summary_report(successful_files: List[str], failed_files: List[str], output_dir: Path):
    report = f"""
    PDF Processing Summary Report
    ============================
    Total files processed: {len(successful_files) + len(failed_files)}
    Successfully processed: {len(successful_files)}
    Failed to process: {len(failed_files)}

    Failed files:
    {', '.join(failed_files)}
    """

    report_path = output_dir / 'summary_report.txt'
    with open(report_path, 'w') as f:
        f.write(report)
