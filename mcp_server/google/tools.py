import logging
import json
import os
from typing import Dict, Any, Optional, Union, List

from mcp import types
from mcp_server.core.mcp_setup import mcp, get_service_context
from mcp_server.google.client import GoogleSheetsClient, GOOGLE_IMPORTS_AVAILABLE
from mcp_server.google.utils import format_data_as_table, parse_json_data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@mcp.tool(name="google_sheets_init", description="Initialize Google Sheets API client.")
async def google_sheets_init(
    credentials_file: str, token_file: Optional[str] = None
) -> List[types.TextContent]:
    """
    Initialize Google Sheets API client.

    Args:
        credentials_file: Path to the credentials.json file
        token_file: Optional path to the token.json file (if not provided, will be created in the same directory as credentials)

    Returns:
        List of TextContent với success status and message
    """
    try:
        if not GOOGLE_IMPORTS_AVAILABLE:
            return [types.TextContent(
                type="text",
                text=(
                    "Google API libraries not available. Install with: "
                    "pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client"
                )
            )]

        context = await get_service_context()

        if not os.path.isabs(credentials_file):
            credentials_file = os.path.join(context.work_directory, credentials_file)

        if token_file and not os.path.isabs(token_file):
            token_file = os.path.join(context.work_directory, token_file)

        sheets_client = GoogleSheetsClient(
            credentials_file=credentials_file, token_file=token_file
        )

        if sheets_client.authenticate():
            context.sheets_client = sheets_client
            return [types.TextContent(
                type="text",
                text="Google Sheets client initialized successfully"
            )]
        else:
            return [types.TextContent(
                type="text",
                text="Failed to authenticate with Google Sheets API"
            )]
            
    except Exception as e:
        error_msg = f"Error initializing Google Sheets client: {str(e)}"
        logger.error(error_msg)
        return [types.TextContent(
            type="text",
            text=error_msg
        )]


@mcp.tool(name="google_sheets_read", description="Read data from a Google Sheet.")
async def google_sheets_read(
    spreadsheet_id: str,
    range_name: str,
    include_headers: bool = True,
    as_json: bool = True,
) -> List[types.TextContent]:
    """
    Read data from a Google Sheet.

    Args:
        spreadsheet_id: ID of the Google Sheet (from the URL)
        range_name: Range to read (e.g., 'Sheet1!A1:D10')
        include_headers: Whether to include headers in the response
        as_json: Whether to return the data as JSON (if False, returns a formatted table)

    Returns:
        List of TextContent với the data from the sheet and metadata
    """
    try:
        context = await get_service_context()

        if not context.sheets_client:
            return [types.TextContent(
                type="text",
                text="Error: Google Sheets client not initialized. Use google_sheets_init first."
            )]

        data = context.sheets_client.read_sheet(spreadsheet_id, range_name, include_headers)

        if not data:
            return [types.TextContent(
                type="text",
                text="No data found in the specified range."
            )]

        if as_json:
            if include_headers and len(data) > 1:
                headers = data[0]
                rows = []
                for row in data[1:]:
                    row_padded = row + [""] * (len(headers) - len(row))
                    rows.append(dict(zip(headers, row_padded[: len(headers)])))

                result = {
                    "success": True,
                    "data": rows,
                    "rows": len(rows),
                    "headers": headers,
                }
            else:
                result = {"success": True, "data": data, "rows": len(data)}
        else:
            result = {
                "success": True,
                "data": format_data_as_table(data),
                "rows": len(data) - (1 if include_headers else 0),
            }

        return [types.TextContent(
            type="text",
            text=json.dumps(result, indent=2)
        )]
        
    except Exception as e:
        error_msg = f"Error reading Google Sheet: {str(e)}"
        logger.error(error_msg)
        return [types.TextContent(
            type="text",
            text=f"Error: {error_msg}"
        )]


@mcp.tool(
    name="google_sheets_write",
    description="Write data to a Google Sheet, replacing existing data.",
)
async def google_sheets_write(
    spreadsheet_id: str, range_name: str, data: Union[List[List[Any]], str]
) -> List[types.TextContent]:
    """
    Write data to a Google Sheet, replacing existing data in the range.

    Args:
        spreadsheet_id: ID of the Google Sheet (from the URL)
        range_name: Range to write to (e.g., 'Sheet1!A1')
        data: Data to write, either as a 2D list or a JSON string representing a 2D list

    Returns:
        List of TextContent với the response from the API
    """
    try:
        context = await get_service_context()

        if not context.sheets_client:
            return [types.TextContent(
                type="text",
                text="Error: Google Sheets client not initialized. Use google_sheets_init first."
            )]

        values = parse_json_data(data) if isinstance(data, str) else data

        if not values:
            return [types.TextContent(
                type="text",
                text="Error: No valid data provided for writing"
            )]

        result = context.sheets_client.write_sheet(spreadsheet_id, range_name, values)

        if "error" in result:
            return [types.TextContent(
                type="text",
                text=f"Error: {result['error']}"
            )]

        response = {
            "success": True,
            "updated_range": result.get("updatedRange", ""),
            "updated_rows": result.get("updatedRows", 0),
            "updated_cells": result.get("updatedCells", 0),
        }

        return [types.TextContent(
            type="text",
            text=json.dumps(response, indent=2)
        )]
        
    except Exception as e:
        error_msg = f"Error writing to Google Sheet: {str(e)}"
        logger.error(error_msg)
        return [types.TextContent(
            type="text",
            text=f"Error: {error_msg}"
        )]


@mcp.tool(name="google_sheets_append", description="Append data to a Google Sheet.")
async def google_sheets_append(
    spreadsheet_id: str, range_name: str, data: Union[List[List[Any]], str]
) -> List[types.TextContent]:
    """
    Append data to a Google Sheet.

    Args:
        spreadsheet_id: ID of the Google Sheet (from the URL)
        range_name: Range to append to (e.g., 'Sheet1!A1')
        data: Data to append, either as a 2D list or a JSON string representing a 2D list

    Returns:
        List of TextContent với the response from the API
    """
    try:
        context = await get_service_context()

        if not context.sheets_client:
            return [types.TextContent(
                type="text",
                text="Error: Google Sheets client not initialized. Use google_sheets_init first."
            )]

        values = parse_json_data(data) if isinstance(data, str) else data

        if not values:
            return [types.TextContent(
                type="text",
                text="Error: No valid data provided for appending"
            )]

        result = context.sheets_client.append_sheet(spreadsheet_id, range_name, values)

        if "error" in result:
            return [types.TextContent(
                type="text",
                text=f"Error: {result['error']}"
            )]

        response = {
            "success": True,
            "updates": {
                "spreadsheet_id": result.get("spreadsheetId", ""),
                "updated_range": result.get("updates", {}).get("updatedRange", ""),
                "updated_rows": result.get("updates", {}).get("updatedRows", 0),
                "updated_cells": result.get("updates", {}).get("updatedCells", 0),
            },
        }

        return [types.TextContent(
            type="text",
            text=json.dumps(response, indent=2)
        )]
        
    except Exception as e:
        error_msg = f"Error appending to Google Sheet: {str(e)}"
        logger.error(error_msg)
        return [types.TextContent(
            type="text",
            text=f"Error: {error_msg}"
        )]


@mcp.tool(name="google_sheets_clear", description="Clear a range in a Google Sheet.")
async def google_sheets_clear(spreadsheet_id: str, range_name: str) -> List[types.TextContent]:
    """
    Clear a range in a Google Sheet.

    Args:
        spreadsheet_id: ID of the Google Sheet (from the URL)
        range_name: Range to clear (e.g., 'Sheet1!A1:D10')

    Returns:
        List of TextContent với the response from the API
    """
    try:
        context = await get_service_context()

        if not context.sheets_client:
            return [types.TextContent(
                type="text",
                text="Error: Google Sheets client not initialized. Use google_sheets_init first."
            )]

        result = context.sheets_client.clear_sheet(spreadsheet_id, range_name)

        if "error" in result:
            return [types.TextContent(
                type="text",
                text=f"Error: {result['error']}"
            )]

        response = {
            "success": True, 
            "cleared_range": result.get("clearedRange", "")
        }

        return [types.TextContent(
            type="text",
            text=json.dumps(response, indent=2)
        )]
        
    except Exception as e:
        error_msg = f"Error clearing range in Google Sheet: {str(e)}"
        logger.error(error_msg)
        return [types.TextContent(
            type="text",
            text=f"Error: {error_msg}"
        )]


@mcp.tool(
    name="google_sheets_create_sheet",
    description="Create a new sheet (tab) in an existing spreadsheet.",
)
async def google_sheets_create_sheet(spreadsheet_id: str, title: str) -> List[types.TextContent]:
    """
    Create a new sheet (tab) in an existing spreadsheet.

    Args:
        spreadsheet_id: ID of the Google Sheet (from the URL)
        title: Title for the new sheet

    Returns:
        List of TextContent với the response from the API
    """
    try:
        context = await get_service_context()

        if not context.sheets_client:
            return [types.TextContent(
                type="text",
                text="Error: Google Sheets client not initialized. Use google_sheets_init first."
            )]

        result = context.sheets_client.create_sheet(spreadsheet_id, title)

        if "error" in result:
            return [types.TextContent(
                type="text",
                text=f"Error: {result['error']}"
            )]

        replies = result.get("replies", [])
        if replies and "addSheet" in replies[0]:
            sheet_props = replies[0]["addSheet"]["properties"]
            response = {
                "success": True,
                "sheet_id": sheet_props.get("sheetId", ""),
                "title": sheet_props.get("title", ""),
                "index": sheet_props.get("index", 0),
            }
        else:
            response = {"success": True, "result": result}

        return [types.TextContent(
            type="text",
            text=json.dumps(response, indent=2)
        )]
        
    except Exception as e:
        error_msg = f"Error creating sheet in Google Spreadsheet: {str(e)}"
        logger.error(error_msg)
        return [types.TextContent(
            type="text",
            text=f"Error: {error_msg}"
        )]


@mcp.tool(
    name="google_sheets_get_sheets",
    description="Get information about sheets in a spreadsheet.",
)
async def google_sheets_get_sheets(spreadsheet_id: str) -> List[types.TextContent]:
    """
    Get information about sheets (tabs) in a spreadsheet.

    Args:
        spreadsheet_id: ID of the Google Sheet (from the URL)

    Returns:
        List of TextContent với the response from the API
    """
    try:
        context = await get_service_context()

        if not context.sheets_client:
            return [types.TextContent(
                type="text",
                text="Error: Google Sheets client not initialized. Use google_sheets_init first."
            )]

        result = context.sheets_client.get_sheets(spreadsheet_id)

        if "error" in result:
            return [types.TextContent(
                type="text",
                text=f"Error: {result['error']}"
            )]

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

        response = {
            "success": True,
            "spreadsheet_id": result.get("spreadsheetId", ""),
            "title": result.get("properties", {}).get("title", ""),
            "sheets": sheets,
        }

        return [types.TextContent(
            type="text",
            text=json.dumps(response, indent=2)
        )]
        
    except Exception as e:
        error_msg = f"Error getting sheets information: {str(e)}"
        logger.error(error_msg)
        return [types.TextContent(
            type="text",
            text=f"Error: {error_msg}"
        )]
