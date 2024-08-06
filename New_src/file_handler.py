import json
from typing import List, Dict, Any, Tuple
from typing import List, Any
from pathlib import Path
import pandas as pd
import logging
from collections import defaultdict
import html

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

def save_elements_data(df: pd.DataFrame, output_folder: Path):
    csv_path = output_folder / "elements_data.csv"
    df.to_csv(csv_path, index=False)

def save_metadata_json(metadata: List[Dict[str, Any]], output_folder: Path):
    json_path = output_folder / "all_elements_metadata.json"
    with open(json_path, 'w') as f:
        json.dump(metadata, f, indent=2)

def save_metadata_html(metadata: List[Dict[str, Any]], output_folder: Path):
    try:
        html_path = output_folder / "all_elements_metadata.html"

        # Group elements by page number
        pages = defaultdict(list)
        for elem in metadata:
            if elem['category'] == 'PageBreak':
                # Add page break to the previous page
                if pages:
                    pages[max(pages.keys())].append(elem)
            else:
                page_num = elem.get('page_number')
                if page_num is not None:
                    pages[page_num].append(elem)
                else:
                    logger.warning(f"Element with id {elem.get('id')} has no page number. Skipping.")

        # Helper function to get element by category for a specific page
        def get_element_by_category(elements: List[Dict[str, Any]], category: str) -> Dict[str, Any]:
            return next((elem for elem in elements if elem['category'] == category), None)

        # Helper function to get all elements by category for a specific page
        def get_elements_by_category(elements: List[Dict[str, Any]], category: str) -> List[Dict[str, Any]]:
            return [elem for elem in elements if elem['category'] == category]

        # Helper function to render an element based on its category
        def render_element(elem: Dict[str, Any]) -> str:
            category = elem['category']
            if category in ['Header', 'Title']:
                return f'<div class="{category.lower()}">{html.escape(elem["text"])}</div>'
            elif category == 'NarrativeText':
                return f'<div class="narrative-text">{html.escape(elem["text"])}</div>'
            elif category == 'Table':
                table_html = f'<div class="table-container">'
                if elem.get('parent_id'):
                    table_html += f'<div class="table-title">{html.escape(elem["parent_id"])}</div>'
                if elem.get('text_as_html'):
                    table_html += elem['text_as_html']
                else:
                    logger.warning(f"Table with id {elem.get('id')} has no HTML content. Skipping.")
                table_html += '</div>'
                return table_html
            elif category == 'Image':
                # Assuming 'text' field contains image description or alt text
                return f'<div class="image-container"><img src="{html.escape(elem.get("src", ""))}" alt="{html.escape(elem["text"])}" /></div>'
            else:
                # For any other categories, render as a generic div with the category as the class
                return f'<div class="{category.lower()}">{html.escape(elem["text"])}</div>'

        html_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Document</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    margin: 0;
                    padding: 20px;
                }
                .header, .title {
                    font-size: 24px;
                    font-weight: bold;
                    margin-bottom: 20px;
                }
                .title {
                    font-size: 20px;
                }
                .narrative-text {
                    margin-bottom: 15px;
                }
                .table-container {
                    margin-bottom: 20px;
                }
                table {
                    border-collapse: collapse;
                    width: 100%;
                }
                th, td {
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
                }
                th {
                    background-color: #f2f2f2;
                }
                .page-break {
                    page-break-before: always;
                    margin-top: 30px;
                }
                .image-container {
                    margin-bottom: 15px;
                }
                img {
                    max-width: 100%;
                    height: auto;
                }
            </style>
        </head>
        <body>
        """

        for page_num, elements in sorted(pages.items()):
            if page_num > 1:
                html_content += '<div class="page-break"></div>'

            html_content += f'<h1>Page {page_num}</h1>'

            # Render all elements on the page
            for elem in elements:
                if elem['category'] != 'PageBreak':
                    html_content += render_element(elem)

            # Check for page break
            if get_element_by_category(elements, 'PageBreak'):
                html_content += '<div class="page-break"></div>'

        html_content += """
        </body>
        </html>
        """

        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        logger.info(f"HTML file created: {html_path}")

    except Exception as e:
        logger.error(f"An error occurred while creating the HTML file: {str(e)}")
        raise

def save_tables(tables: List[Any], output_folder: Path):
    # Group tables by parent ID
    grouped_tables = defaultdict(list)
    for table in tables:
        parent_id = getattr(table.metadata, 'parent_id', 'unknown_parent')
        grouped_tables[parent_id].append(table)

    for parent_id, table_group in grouped_tables.items():
        try:
            combined_html_content = ""
            page_numbers = set()

            for i, table in enumerate(table_group):
                table_html = getattr(table.metadata, 'text_as_html', None)
                page_number = getattr(table.metadata, 'page_number', f'unknown_page_{i}')
                page_numbers.add(str(page_number))

                if table_html is None:
                    logger.warning(f"No HTML data for table in group {parent_id} on page {page_number}. Skipping.")
                    continue

                # Append HTML content for combined HTML file
                combined_html_content += f"<h2>Table Part {i + 1} (Page {page_number})</h2>\n{table_html}\n"

                # Process and save individual CSV file
                try:
                    tables_df = pd.read_html(table_html)
                    if tables_df:
                        current_df = tables_df[0]

                        logger.info(f"Table {i} in group {parent_id} has shape: {current_df.shape}")

                        # Add metadata columns to individual table
                        current_df["Parent ID"] = parent_id
                        current_df["Page Number"] = page_number

                        # Save individual CSV
                        csv_filename = f"table_{parent_id}_page{page_number}_part{i + 1}.csv"
                        csv_path = output_folder / csv_filename
                        current_df.to_csv(csv_path, index=False)
                        logger.info(f"Saved individual CSV table to {csv_path}")
                    else:
                        logger.warning(f"No tables found in HTML for table in group {parent_id} on page {page_number}")
                except ValueError as e:
                    logger.error(f"Error parsing HTML table: {str(e)}")
                    logger.debug(f"Problematic HTML content: {table_html}")

            # Create and save combined HTML file
            if combined_html_content:
                html_content = f"""
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Combined Table - Parent ID: {html.escape(parent_id)}</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; }}
                        h1 {{ color: #333; }}
                        h2 {{ color: #666; }}
                        table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
                        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                        th {{ background-color: #f2f2f2; }}
                    </style>
                </head>
                <body>
                    <h1>Combined Table - Parent ID: {html.escape(parent_id)}</h1>
                    <p>Pages: {', '.join(sorted(page_numbers))}</p>
                    {combined_html_content}
                </body>
                </html>
                """

                html_filename = f"table_{parent_id}_pages{'_'.join(sorted(page_numbers))}.html"
                html_path = output_folder / html_filename
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                logger.info(f"Saved combined HTML table to {html_path}")
            else:
                logger.warning(f"No valid data to save for table group {parent_id}")

        except Exception as e:
            logger.error(f"Error processing table group {parent_id}: {str(e)}", exc_info=True)

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
