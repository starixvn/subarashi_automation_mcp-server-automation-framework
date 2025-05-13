"""
MCP tools for Google Sheets API integration.
"""

import logging
import json
import os
from typing import Dict, Any, Optional, Union, List

from mcp_tools.server.core.mcp_setup import mcp, work_dir
from mcp_tools.server.google.client import GoogleSheetsClient, GOOGLE_IMPORTS_AVAILABLE
from mcp_tools.server.google.utils import format_data_as_table, parse_json_data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global Google Sheets client
sheets_client = None


@mcp.tool(name="Google-Sheets-Init", description="Initialize Google Sheets API client.")
async def google_sheets_init(
    credentials_file: str, token_file: Optional[str] = None
) -> Dict[str, Any]:
    """
    Initialize Google Sheets API client.

    Args:
        credentials_file: Path to the credentials.json file
        token_file: Optional path to the token.json file (if not provided, will be created in the same directory as credentials)

    Returns:
        Dictionary with success status and client object
    """
    global sheets_client

    if not GOOGLE_IMPORTS_AVAILABLE:
        return {
            "success": False,
            "message": (
                "Google API libraries not available. Install with: "
                "pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client"
            ),
        }

    try:
        # If credentials file is relative path, make it relative to the workspace root
        if not os.path.isabs(credentials_file):
            credentials_file = os.path.join(work_dir, credentials_file)

        if token_file and not os.path.isabs(token_file):
            token_file = os.path.join(work_dir, token_file)

        sheets_client = GoogleSheetsClient(
            credentials_file=credentials_file, token_file=token_file
        )

        if sheets_client.authenticate():
            return {
                "success": True,
                "client": sheets_client,
                "message": "Google Sheets client initialized successfully",
            }
        else:
            return {
                "success": False,
                "message": "Failed to authenticate with Google Sheets API",
            }
    except Exception as e:
        error_msg = f"Error initializing Google Sheets client: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "message": error_msg}


@mcp.tool(name="Google-Sheets-Read", description="Read data from a Google Sheet.")
async def google_sheets_read(
    spreadsheet_id: str,
    range_name: str,
    include_headers: bool = True,
    as_json: bool = True,
) -> Dict[str, Any]:
    """
    Read data from a Google Sheet.

    Args:
        spreadsheet_id: ID of the Google Sheet (from the URL)
        range_name: Range to read (e.g., 'Sheet1!A1:D10')
        include_headers: Whether to include headers in the response
        as_json: Whether to return the data as JSON (if False, returns a formatted table)

    Returns:
        Dictionary with the data from the sheet and metadata
    """
    global sheets_client

    if not sheets_client:
        return {
            "success": False,
            "message": "Error: Google Sheets client not initialized. Use Google-Sheets-Init first.",
        }

    try:
        data = sheets_client.read_sheet(spreadsheet_id, range_name, include_headers)

        if not data:
            return {
                "success": False,
                "message": "No data found in the specified range.",
            }

        if as_json:
            # If the first row contains headers, use them as keys
            if include_headers and len(data) > 1:
                headers = data[0]
                rows = []
                for row in data[1:]:
                    # Ensure row has same length as headers by padding with empty strings
                    row_padded = row + [""] * (len(headers) - len(row))
                    rows.append(dict(zip(headers, row_padded[: len(headers)])))

                return {
                    "success": True,
                    "data": rows,
                    "rows": len(rows),
                    "headers": headers,
                }
            else:
                # Return as list of lists without processing
                return {"success": True, "data": data, "rows": len(data)}
        else:
            # Format as markdown table
            return {
                "success": True,
                "data": format_data_as_table(data),
                "rows": len(data) - (1 if include_headers else 0),
            }
    except Exception as e:
        error_msg = f"Error reading Google Sheet: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "message": error_msg}


@mcp.tool(
    name="Google-Sheets-Write",
    description="Write data to a Google Sheet, replacing existing data.",
)
async def google_sheets_write(
    spreadsheet_id: str, range_name: str, data: Union[List[List[Any]], str]
) -> Dict[str, Any]:
    """
    Write data to a Google Sheet, replacing existing data in the range.

    Args:
        spreadsheet_id: ID of the Google Sheet (from the URL)
        range_name: Range to write to (e.g., 'Sheet1!A1')
        data: Data to write, either as a 2D list or a JSON string representing a 2D list

    Returns:
        Dictionary with the response from the API
    """
    global sheets_client

    if not sheets_client:
        return {
            "success": False,
            "message": "Error: Google Sheets client not initialized. Use Google-Sheets-Init first.",
        }

    try:
        values = parse_json_data(data) if isinstance(data, str) else data

        if not values:
            return {"success": False, "message": "No valid data provided for writing"}

        result = sheets_client.write_sheet(spreadsheet_id, range_name, values)

        if "error" in result:
            return {"success": False, "message": result["error"]}

        return {
            "success": True,
            "updated_range": result.get("updatedRange", ""),
            "updated_rows": result.get("updatedRows", 0),
            "updated_cells": result.get("updatedCells", 0),
        }
    except Exception as e:
        error_msg = f"Error writing to Google Sheet: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "message": error_msg}


@mcp.tool(name="Google-Sheets-Append", description="Append data to a Google Sheet.")
async def google_sheets_append(
    spreadsheet_id: str, range_name: str, data: Union[List[List[Any]], str]
) -> Dict[str, Any]:
    """
    Append data to a Google Sheet.

    Args:
        spreadsheet_id: ID of the Google Sheet (from the URL)
        range_name: Range to append to (e.g., 'Sheet1!A1')
        data: Data to append, either as a 2D list or a JSON string representing a 2D list

    Returns:
        Dictionary with the response from the API
    """
    global sheets_client

    if not sheets_client:
        return {
            "success": False,
            "message": "Error: Google Sheets client not initialized. Use Google-Sheets-Init first.",
        }

    try:
        values = parse_json_data(data) if isinstance(data, str) else data

        if not values:
            return {"success": False, "message": "No valid data provided for appending"}

        result = sheets_client.append_sheet(spreadsheet_id, range_name, values)

        if "error" in result:
            return {"success": False, "message": result["error"]}

        return {
            "success": True,
            "updates": {
                "spreadsheet_id": result.get("spreadsheetId", ""),
                "updated_range": result.get("updates", {}).get("updatedRange", ""),
                "updated_rows": result.get("updates", {}).get("updatedRows", 0),
                "updated_cells": result.get("updates", {}).get("updatedCells", 0),
            },
        }
    except Exception as e:
        error_msg = f"Error appending to Google Sheet: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "message": error_msg}


@mcp.tool(name="Google-Sheets-Clear", description="Clear a range in a Google Sheet.")
async def google_sheets_clear(spreadsheet_id: str, range_name: str) -> Dict[str, Any]:
    """
    Clear a range in a Google Sheet.

    Args:
        spreadsheet_id: ID of the Google Sheet (from the URL)
        range_name: Range to clear (e.g., 'Sheet1!A1:D10')

    Returns:
        Dictionary with the response from the API
    """
    global sheets_client

    if not sheets_client:
        return {
            "success": False,
            "message": "Error: Google Sheets client not initialized. Use Google-Sheets-Init first.",
        }

    try:
        result = sheets_client.clear_range(spreadsheet_id, range_name)

        if "error" in result:
            return {"success": False, "message": result["error"]}

        return {"success": True, "cleared_range": result.get("clearedRange", "")}
    except Exception as e:
        error_msg = f"Error clearing range in Google Sheet: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "message": error_msg}


@mcp.tool(
    name="Google-Sheets-CreateSheet",
    description="Create a new sheet (tab) in an existing spreadsheet.",
)
async def google_sheets_create_sheet(spreadsheet_id: str, title: str) -> Dict[str, Any]:
    """
    Create a new sheet (tab) in an existing spreadsheet.

    Args:
        spreadsheet_id: ID of the Google Sheet (from the URL)
        title: Title for the new sheet

    Returns:
        Dictionary with the response from the API
    """
    global sheets_client

    if not sheets_client:
        return {
            "success": False,
            "message": "Error: Google Sheets client not initialized. Use Google-Sheets-Init first.",
        }

    try:
        result = sheets_client.create_sheet(spreadsheet_id, title)

        if "error" in result:
            return {"success": False, "message": result["error"]}

        replies = result.get("replies", [])
        if replies and "addSheet" in replies[0]:
            sheet_props = replies[0]["addSheet"]["properties"]
            return {
                "success": True,
                "sheet_id": sheet_props.get("sheetId", ""),
                "title": sheet_props.get("title", ""),
                "index": sheet_props.get("index", 0),
            }

        return {"success": True, "result": result}
    except Exception as e:
        error_msg = f"Error creating sheet in Google Spreadsheet: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "message": error_msg}


@mcp.tool(
    name="Google-Sheets-GetSheets",
    description="Get information about sheets in a spreadsheet.",
)
async def google_sheets_get_sheets(spreadsheet_id: str) -> Dict[str, Any]:
    """
    Get information about sheets (tabs) in a spreadsheet.

    Args:
        spreadsheet_id: ID of the Google Sheet (from the URL)

    Returns:
        Dictionary with the response from the API
    """
    global sheets_client

    if not sheets_client:
        return {
            "success": False,
            "message": "Error: Google Sheets client not initialized. Use Google-Sheets-Init first.",
        }

    try:
        result = sheets_client.get_sheets(spreadsheet_id)

        if "error" in result:
            return {"success": False, "message": result["error"]}

        sheets = []
        for sheet in result.get("sheets", []):
            props = sheet.get("properties", {})
            sheets.append(
                {
                    "sheet_id": props.get("sheetId", ""),
                    "title": props.get("title", ""),
                    "index": props.get("index", 0),
                    "row_count": props.get("gridProperties", {}).get("rowCount", 0),
                    "column_count": props.get("gridProperties", {}).get(
                        "columnCount", 0
                    ),
                }
            )

        return {
            "success": True,
            "spreadsheet_id": result.get("spreadsheetId", ""),
            "title": result.get("properties", {}).get("title", ""),
            "sheets": sheets,
        }
    except Exception as e:
        error_msg = f"Error getting sheets information: {str(e)}"
        logger.error(error_msg)
        return {"success": False, "message": error_msg}
