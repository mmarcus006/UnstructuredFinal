from typing import Any, Dict, List, Tuple
import pandas as pd
from unstructured.documents.coordinates import RelativeCoordinateSystem

def extract_element_metadata(element: Any) -> Dict[str, Any]:
    metadata = {
        "id": getattr(element, 'id', None),
        "text": getattr(element, 'text', ''),
        "category": getattr(element, 'category', 'Unknown'),
        "filename": getattr(element.metadata, 'filename', None),
        "parent_id": getattr(element.metadata, 'parent_id', None),
        "coordinates": getattr(element.metadata, 'coordinates', None),
        "detection_class_prob": getattr(element.metadata, 'detection_class_prob', None),
        "page_number": getattr(element.metadata, 'page_number', None),
    }

    try:
        if hasattr(element.metadata, 'coordinates') and element.metadata.coordinates:
            pixel_coords = element.metadata.coordinates
            metadata["coordinates"] = {
                "points": pixel_coords.points,
                "system": {
                    "name": pixel_coords.system.name,
                    "orientation": pixel_coords.system.orientation,
                    "width": pixel_coords.system.width,
                    "height": pixel_coords.system.height,
                }
            }

            relative_coords = element.convert_coordinates_to_new_system(RelativeCoordinateSystem())
            metadata["relative_coordinates"] = {
                "points": relative_coords.points,
                "system": {
                    "name": relative_coords.system.name,
                    "orientation": relative_coords.system.orientation,
                    "width": relative_coords.system.width,
                    "height": relative_coords.system.height,
                }
            }
    except AttributeError:
        metadata["coordinates"] = None
        metadata["relative_coordinates"] = None

    metadata["detection_class_prob"] = getattr(element.metadata, 'detection_class_prob', None)

    if getattr(element, 'category', '').lower() == "table":
        metadata["text_as_html"] = getattr(element.metadata, 'text_as_html', None)

    return metadata

def process_elements(elements: List[Any]) -> Tuple[pd.DataFrame, List[Any], List[Dict[str, Any]]]:
    all_elements_df = pd.DataFrame()
    tables = []
    all_elements_metadata = []

    for element in elements:
        element_metadata = extract_element_metadata(element)
        all_elements_metadata.append(element_metadata)

        if element.metadata:
            new_row = pd.DataFrame({
                "Page Number": [getattr(element.metadata, 'page_number', None)],
                "Element ID": [getattr(element, 'id', None)],
                "Parent Element": [getattr(element.metadata, 'parent_id', None)],
                "Coordinates": [getattr(element.metadata, 'coordinates', None)],
                "Detection Class Probability": [getattr(element.metadata, 'detection_class_prob', None)],
                "Category": [getattr(element, 'category', 'Unknown')],
                "Text": [getattr(element, 'text', '')],
                "Table as HTML": [getattr(element.metadata, 'text_as_html', None) if getattr(element, 'category',
                                                                                            '').lower() == 'table' else None]
            })
            all_elements_df = pd.concat([all_elements_df, new_row], ignore_index=True)

        if element.category == "Table":
            tables.append(element)

    return all_elements_df, tables, all_elements_metadata
