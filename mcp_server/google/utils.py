"""
Utility functions for Google Sheets integration.
"""

import json
import logging
from typing import List, Any, Dict, Optional, Union

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def format_data_as_table(data: List[List[Any]], include_headers: bool = True) -> str:
    """
    Format data as a markdown table for display.

    Args:
        data: Data to format
        include_headers: Whether to include headers in the table

    Returns:
        Formatted table string
    """
    if not data:
        return "No data found"

    col_widths = []
    for i in range(max(len(row) for row in data)):
        col_widths.append(max(len(str(row[i])) if i < len(row) else 0 for row in data))

    result = []

    if include_headers and len(data) > 0:
        header = data[0]
        header_str = (
            "| "
            + " | ".join(str(val).ljust(col_widths[i]) for i, val in enumerate(header))
            + " |"
        )
        result.append(header_str)
        result.append("|" + "".join("-" * (width + 2) + "|" for width in col_widths))
        data = data[1:]

    for row in data:
        row_str = (
            "| "
            + " | ".join(
                (
                    str(row[i]).ljust(col_widths[i])
                    if i < len(row)
                    else "".ljust(col_widths[i])
                )
                for i in range(len(col_widths))
            )
            + " |"
        )
        result.append(row_str)

    return "\n".join(result)


def parse_json_data(data_str: str) -> List[List[Any]]:
    """
    Parse JSON data into a 2D list suitable for Google Sheets.

    Args:
        data_str: JSON string representing data

    Returns:
        2D list of values
    """
    try:
        parsed_data = json.loads(data_str)

        if (
            parsed_data
            and isinstance(parsed_data, list)
            and isinstance(parsed_data[0], dict)
        ):
            all_keys = []
            for item in parsed_data:
                for key in item.keys():
                    if key not in all_keys:
                        all_keys.append(key)

            values = [all_keys]
            for item in parsed_data:
                row = [item.get(key, "") for key in all_keys]
                values.append(row)
            return values
        else:
            return parsed_data
    except json.JSONDecodeError:
        raise ValueError("Invalid JSON data format")


def extract_sheet_id_from_response(response: Dict[str, Any]) -> Optional[str]:
    """
    Extract sheet ID from Google Sheets API response.

    Args:
        response: Response from Google Sheets API

    Returns:
        Sheet ID if found, None otherwise
    """
    try:
        return (
            response.get("replies", [{}])[0]
            .get("addSheet", {})
            .get("properties", {})
            .get("sheetId")
        )
    except (IndexError, AttributeError):
        return None
