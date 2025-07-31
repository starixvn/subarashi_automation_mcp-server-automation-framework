import os
import json
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from core.tool_schema import (
    ToolInputSchema,
    ToolResult,
    ToolActionResult,
    define_tool_factory,
    ToolCapability,
    ToolType,
    Tool,
    ToolSchema,
)


SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

SERVICE_ACCOUNT_FILE = "config/keys/service-account.json"


class CreateSpreadsheetInput(ToolInputSchema):
    title: str = Field(description="Title of the new spreadsheet")
    sheet_names: Optional[List[str]] = Field(
        default=None, description="Names of initial sheets to create"
    )


class OpenSpreadsheetInput(ToolInputSchema):
    spreadsheet_id: Optional[str] = Field(
        default=None, description="Google Sheets spreadsheet ID"
    )
    url: Optional[str] = Field(default=None, description="Google Sheets URL")


class ShareSpreadsheetInput(ToolInputSchema):
    spreadsheet_id: str = Field(description="Spreadsheet ID to share")
    email: str = Field(description="Email address to share with")
    role: str = Field(
        default="writer",
        description="Permission role: owner, writer, commenter, reader",
    )


class ListSpreadsheetsInput(ToolInputSchema):
    max_results: Optional[int] = Field(
        default=50, description="Maximum number of spreadsheets to return"
    )


class CreateWorksheetInput(ToolInputSchema):
    spreadsheet_id: str = Field(description="Spreadsheet ID")
    title: str = Field(description="Title of the new worksheet")
    rows: Optional[int] = Field(default=1000, description="Number of rows")
    columns: Optional[int] = Field(default=26, description="Number of columns")


class DeleteWorksheetInput(ToolInputSchema):
    spreadsheet_id: str = Field(description="Spreadsheet ID")
    sheet_id: int = Field(description="Sheet ID to delete")


class RenameWorksheetInput(ToolInputSchema):
    spreadsheet_id: str = Field(description="Spreadsheet ID")
    sheet_id: int = Field(description="Sheet ID to rename")
    new_title: str = Field(description="New title for the worksheet")


class ListWorksheetsInput(ToolInputSchema):
    spreadsheet_id: str = Field(description="Spreadsheet ID")


class ReadRangeInput(ToolInputSchema):
    spreadsheet_id: str = Field(description="Spreadsheet ID")
    range_name: str = Field(description="Range to read (e.g., 'Sheet1!A1:C10')")
    major_dimension: Optional[str] = Field(
        default="ROWS", description="Major dimension: ROWS or COLUMNS"
    )


class WriteRangeInput(ToolInputSchema):
    spreadsheet_id: str = Field(description="Spreadsheet ID")
    range_name: str = Field(description="Range to write (e.g., 'Sheet1!A1:C10')")
    values: List[Any] = Field(description="List of values to write")
    major_dimension: Optional[str] = Field(
        default="ROWS", description="Major dimension: ROWS or COLUMNS"
    )


class UpdateCellInput(ToolInputSchema):
    spreadsheet_id: str = Field(description="Spreadsheet ID")
    range_name: str = Field(description="Single cell range (e.g., 'Sheet1!A1')")
    value: Any = Field(description="Value to write to the cell")


class AppendDataInput(ToolInputSchema):
    spreadsheet_id: str = Field(description="Spreadsheet ID")
    range_name: str = Field(description="Range to append to (e.g., 'Sheet1!A:A')")
    values: List[Any] = Field(description="List of values to append")
    value_input_option: Optional[str] = Field(
        default="RAW", description="RAW or USER_ENTERED"
    )


class ClearRangeInput(ToolInputSchema):
    spreadsheet_id: str = Field(description="Spreadsheet ID")
    range_name: str = Field(description="Range to clear (e.g., 'Sheet1!A1:C10')")


class FormatCellsInput(ToolInputSchema):
    spreadsheet_id: str = Field(description="Spreadsheet ID")
    range_name: str = Field(description="Range to format")
    bold: Optional[bool] = Field(default=None, description="Make text bold")
    italic: Optional[bool] = Field(default=None, description="Make text italic")
    font_size: Optional[int] = Field(default=None, description="Font size")
    background_color: Optional[Dict[str, float]] = Field(
        default=None, description="Background color RGB (0-1)"
    )
    text_color: Optional[Dict[str, float]] = Field(
        default=None, description="Text color RGB (0-1)"
    )


class MergeCellsInput(ToolInputSchema):
    spreadsheet_id: str = Field(description="Spreadsheet ID")
    range_name: str = Field(description="Range to merge")
    merge_type: Optional[str] = Field(
        default="MERGE_ALL", description="MERGE_ALL, MERGE_COLUMNS, MERGE_ROWS"
    )


class SortRangeInput(ToolInputSchema):
    spreadsheet_id: str = Field(description="Spreadsheet ID")
    range_name: str = Field(description="Range to sort")
    sort_column: int = Field(description="Column index to sort by (0-based)")
    ascending: Optional[bool] = Field(
        default=True, description="Sort in ascending order"
    )


class InsertRowsInput(ToolInputSchema):
    spreadsheet_id: str = Field(description="Spreadsheet ID")
    sheet_id: int = Field(description="Sheet ID")
    start_index: int = Field(description="Start row index (0-based)")
    end_index: int = Field(description="End row index (0-based, exclusive)")


class InsertColumnsInput(ToolInputSchema):
    spreadsheet_id: str = Field(description="Spreadsheet ID")
    sheet_id: int = Field(description="Sheet ID")
    start_index: int = Field(description="Start column index (0-based)")
    end_index: int = Field(description="End column index (0-based, exclusive)")


class DeleteRowsInput(ToolInputSchema):
    spreadsheet_id: str = Field(description="Spreadsheet ID")
    sheet_id: int = Field(description="Sheet ID")
    start_index: int = Field(description="Start row index (0-based)")
    end_index: int = Field(description="End row index (0-based, exclusive)")


class DeleteColumnsInput(ToolInputSchema):
    spreadsheet_id: str = Field(description="Spreadsheet ID")
    sheet_id: int = Field(description="Sheet ID")
    start_index: int = Field(description="Start column index (0-based)")
    end_index: int = Field(description="End column index (0-based, exclusive)")


class FindReplaceInput(ToolInputSchema):
    spreadsheet_id: str = Field(description="Spreadsheet ID")
    find_text: str = Field(description="Text to find")
    replace_text: str = Field(description="Text to replace with")
    sheet_id: Optional[int] = Field(
        default=None, description="Sheet ID to search in (all sheets if None)"
    )
    match_case: Optional[bool] = Field(
        default=False, description="Match case sensitivity"
    )
    match_entire_cell: Optional[bool] = Field(
        default=False, description="Match entire cell content"
    )


class AddFormulaInput(ToolInputSchema):
    spreadsheet_id: str = Field(description="Spreadsheet ID")
    range_name: str = Field(description="Cell range for formula")
    formula: str = Field(description="Formula to add (without = sign)")


class FreezeRowsInput(ToolInputSchema):
    spreadsheet_id: str = Field(description="Spreadsheet ID")
    sheet_id: int = Field(description="Sheet ID")
    frozen_row_count: int = Field(description="Number of rows to freeze")


class FreezeColumnsInput(ToolInputSchema):
    spreadsheet_id: str = Field(description="Spreadsheet ID")
    sheet_id: int = Field(description="Sheet ID")
    frozen_column_count: int = Field(description="Number of columns to freeze")


def get_google_sheets_service():
    credentials = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    service = build("sheets", "v4", credentials=credentials)
    return service


def get_google_drive_service():
    credentials = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    service = build("drive", "v3", credentials=credentials)
    return service


def extract_spreadsheet_id(url_or_id: str) -> str:
    if url_or_id.startswith("https://docs.google.com/spreadsheets/d/"):
        return url_or_id.split("/d/")[1].split("/")[0]
    return url_or_id


@define_tool_factory(
    capability=ToolCapability.GOOGLE_SHEETS,
    name="sheets_create_spreadsheet",
    title="Create Spreadsheet",
    description="Create a new Google Spreadsheet",
    input_schema=CreateSpreadsheetInput,
    tool_type=ToolType.DESTRUCTIVE,
)
def sheets_create_spreadsheet_factory(capture_snapshot: bool) -> Tool:
    async def handle(context, params: Dict[str, Any]) -> ToolResult:
        async def action() -> ToolActionResult:
            try:
                service = get_google_sheets_service()

                spreadsheet_body = {"properties": {"title": params["title"]}}

                if params.get("sheet_names"):
                    spreadsheet_body["sheets"] = []
                    for i, sheet_name in enumerate(params["sheet_names"]):
                        spreadsheet_body["sheets"].append(
                            {
                                "properties": {
                                    "title": sheet_name,
                                    "sheetId": i,
                                    "gridProperties": {
                                        "rowCount": 1000,
                                        "columnCount": 26,
                                    },
                                }
                            }
                        )

                spreadsheet = (
                    service.spreadsheets().create(body=spreadsheet_body).execute()
                )

                spreadsheet_id = spreadsheet.get("spreadsheetId")
                spreadsheet_url = (
                    f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
                )

                return ToolActionResult(
                    content=[
                        {
                            "type": "text",
                            "text": f"Created spreadsheet: {params['title']}\nID: {spreadsheet_id}\nURL: {spreadsheet_url}",
                        }
                    ]
                )

            except HttpError as error:
                return ToolActionResult(
                    content=[
                        {"type": "text", "text": f"Error creating spreadsheet: {error}"}
                    ]
                )

        return ToolResult(
            code=[f"# Creating spreadsheet: {params['title']}"],
            action=action,
            capture_snapshot=False,
            wait_for_network=False,
        )

    schema = ToolSchema(
        name="sheets_create_spreadsheet",
        title="Create Spreadsheet",
        description="Create a new Google Spreadsheet",
        input_schema=CreateSpreadsheetInput,
        tool_type=ToolType.DESTRUCTIVE,
    )

    return Tool(
        capability=ToolCapability.GOOGLE_SHEETS,
        schema=schema,
        handle=handle,
        browser_independent=True,
    )


@define_tool_factory(
    capability=ToolCapability.GOOGLE_SHEETS,
    name="sheets_open_spreadsheet",
    title="Open Spreadsheet",
    description="Open an existing Google Spreadsheet by ID or URL",
    input_schema=OpenSpreadsheetInput,
    tool_type=ToolType.READ_ONLY,
)
def sheets_open_spreadsheet_factory(capture_snapshot: bool) -> Tool:
    async def handle(context, params: Dict[str, Any]) -> ToolResult:
        async def action() -> ToolActionResult:
            try:
                service = get_google_sheets_service()

                spreadsheet_id = None
                if params.get("spreadsheet_id"):
                    spreadsheet_id = params["spreadsheet_id"]
                elif params.get("url"):
                    spreadsheet_id = extract_spreadsheet_id(params["url"])
                else:
                    return ToolActionResult(
                        content=[
                            {
                                "type": "text",
                                "text": "Error: Either spreadsheet_id or url must be provided",
                            }
                        ]
                    )

                spreadsheet = (
                    service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
                )

                title = spreadsheet.get("properties", {}).get("title", "Unknown")
                sheets = spreadsheet.get("sheets", [])
                sheet_names = [
                    sheet.get("properties", {}).get("title", "") for sheet in sheets
                ]

                result_text = f"Opened spreadsheet: {title}\n"
                result_text += f"ID: {spreadsheet_id}\n"
                result_text += f"Sheets: {', '.join(sheet_names)}"

                return ToolActionResult(content=[{"type": "text", "text": result_text}])

            except HttpError as error:
                return ToolActionResult(
                    content=[
                        {"type": "text", "text": f"Error opening spreadsheet: {error}"}
                    ]
                )

        return ToolResult(
            code=[f"# Opening spreadsheet"],
            action=action,
            capture_snapshot=False,
            wait_for_network=False,
        )

    schema = ToolSchema(
        name="sheets_open_spreadsheet",
        title="Open Spreadsheet",
        description="Open an existing Google Spreadsheet by ID or URL",
        input_schema=OpenSpreadsheetInput,
        tool_type=ToolType.READ_ONLY,
    )

    return Tool(
        capability=ToolCapability.GOOGLE_SHEETS,
        schema=schema,
        handle=handle,
        browser_independent=True,
    )


@define_tool_factory(
    capability=ToolCapability.GOOGLE_SHEETS,
    name="sheets_share_spreadsheet",
    title="Share Spreadsheet",
    description="Share a Google Spreadsheet with an email address",
    input_schema=ShareSpreadsheetInput,
    tool_type=ToolType.DESTRUCTIVE,
)
def sheets_share_spreadsheet_factory(capture_snapshot: bool) -> Tool:
    async def handle(context, params: Dict[str, Any]) -> ToolResult:
        async def action() -> ToolActionResult:
            try:
                drive_service = get_google_drive_service()

                permission = {
                    "type": "user",
                    "role": params["role"],
                    "emailAddress": params["email"],
                }

                drive_service.permissions().create(
                    fileId=params["spreadsheet_id"],
                    body=permission,
                    sendNotificationEmail=True,
                ).execute()

                return ToolActionResult(
                    content=[
                        {
                            "type": "text",
                            "text": f"Shared spreadsheet with {params['email']} as {params['role']}",
                        }
                    ]
                )

            except HttpError as error:
                return ToolActionResult(
                    content=[
                        {"type": "text", "text": f"Error sharing spreadsheet: {error}"}
                    ]
                )

        return ToolResult(
            code=[f"# Sharing spreadsheet with {params['email']}"],
            action=action,
            capture_snapshot=False,
            wait_for_network=False,
        )

    schema = ToolSchema(
        name="sheets_share_spreadsheet",
        title="Share Spreadsheet",
        description="Share a Google Spreadsheet with an email address",
        input_schema=ShareSpreadsheetInput,
        tool_type=ToolType.DESTRUCTIVE,
    )

    return Tool(
        capability=ToolCapability.GOOGLE_SHEETS,
        schema=schema,
        handle=handle,
        browser_independent=True,
    )


@define_tool_factory(
    capability=ToolCapability.GOOGLE_SHEETS,
    name="sheets_list_spreadsheets",
    title="List Spreadsheets",
    description="List accessible Google Spreadsheets",
    input_schema=ListSpreadsheetsInput,
    tool_type=ToolType.READ_ONLY,
)
def sheets_list_spreadsheets_factory(capture_snapshot: bool) -> Tool:
    async def handle(context, params: Dict[str, Any]) -> ToolResult:
        async def action() -> ToolActionResult:
            try:
                drive_service = get_google_drive_service()

                query = "mimeType='application/vnd.google-apps.spreadsheet'"
                results = (
                    drive_service.files()
                    .list(
                        q=query,
                        pageSize=params.get("max_results", 50),
                        fields="files(id, name, createdTime, modifiedTime)",
                    )
                    .execute()
                )

                files = results.get("files", [])

                if not files:
                    return ToolActionResult(
                        content=[{"type": "text", "text": "No spreadsheets found"}]
                    )

                result_text = "Accessible Spreadsheets:\n"
                for file in files:
                    result_text += f"- {file['name']} (ID: {file['id']})\n"
                    result_text += f"  Created: {file.get('createdTime', 'Unknown')}\n"
                    result_text += (
                        f"  Modified: {file.get('modifiedTime', 'Unknown')}\n\n"
                    )

                return ToolActionResult(content=[{"type": "text", "text": result_text}])

            except HttpError as error:
                return ToolActionResult(
                    content=[
                        {"type": "text", "text": f"Error listing spreadsheets: {error}"}
                    ]
                )

        return ToolResult(
            code=[f"# Listing spreadsheets"],
            action=action,
            capture_snapshot=False,
            wait_for_network=False,
        )

    schema = ToolSchema(
        name="sheets_list_spreadsheets",
        title="List Spreadsheets",
        description="List accessible Google Spreadsheets",
        input_schema=ListSpreadsheetsInput,
        tool_type=ToolType.READ_ONLY,
    )

    return Tool(
        capability=ToolCapability.GOOGLE_SHEETS,
        schema=schema,
        handle=handle,
        browser_independent=True,
    )


@define_tool_factory(
    capability=ToolCapability.GOOGLE_SHEETS,
    name="sheets_create_worksheet",
    title="Create Worksheet",
    description="Create a new worksheet in an existing spreadsheet",
    input_schema=CreateWorksheetInput,
    tool_type=ToolType.DESTRUCTIVE,
)
def sheets_create_worksheet_factory(capture_snapshot: bool) -> Tool:
    async def handle(context, params: Dict[str, Any]) -> ToolResult:
        async def action() -> ToolActionResult:
            try:
                service = get_google_sheets_service()

                request = {
                    "addSheet": {
                        "properties": {
                            "title": params["title"],
                            "gridProperties": {
                                "rowCount": params.get("rows", 1000),
                                "columnCount": params.get("columns", 26),
                            },
                        }
                    }
                }

                body = {"requests": [request]}

                response = (
                    service.spreadsheets()
                    .batchUpdate(spreadsheetId=params["spreadsheet_id"], body=body)
                    .execute()
                )

                sheet_id = response["replies"][0]["addSheet"]["properties"]["sheetId"]

                return ToolActionResult(
                    content=[
                        {
                            "type": "text",
                            "text": f"Created worksheet: {params['title']} (ID: {sheet_id})",
                        }
                    ]
                )

            except HttpError as error:
                return ToolActionResult(
                    content=[
                        {"type": "text", "text": f"Error creating worksheet: {error}"}
                    ]
                )

        return ToolResult(
            code=[f"# Creating worksheet: {params['title']}"],
            action=action,
            capture_snapshot=False,
            wait_for_network=False,
        )

    schema = ToolSchema(
        name="sheets_create_worksheet",
        title="Create Worksheet",
        description="Create a new worksheet in an existing spreadsheet",
        input_schema=CreateWorksheetInput,
        tool_type=ToolType.DESTRUCTIVE,
    )

    return Tool(
        capability=ToolCapability.GOOGLE_SHEETS,
        schema=schema,
        handle=handle,
        browser_independent=True,
    )


@define_tool_factory(
    capability=ToolCapability.GOOGLE_SHEETS,
    name="sheets_read_range",
    title="Read Range",
    description="Read data from a specific range in a Google Sheet",
    input_schema=ReadRangeInput,
    tool_type=ToolType.READ_ONLY,
)
def sheets_read_range_factory(capture_snapshot: bool) -> Tool:
    async def handle(context, params: Dict[str, Any]) -> ToolResult:
        async def action() -> ToolActionResult:
            try:
                service = get_google_sheets_service()

                result = (
                    service.spreadsheets()
                    .values()
                    .get(
                        spreadsheetId=params["spreadsheet_id"],
                        range=params["range_name"],
                        majorDimension=params.get("major_dimension", "ROWS"),
                    )
                    .execute()
                )

                values = result.get("values", [])

                if not values:
                    return ToolActionResult(
                        content=[
                            {
                                "type": "text",
                                "text": f"No data found in range: {params['range_name']}",
                            }
                        ]
                    )

                result_text = f"Data from range {params['range_name']}:\n"
                for i, row in enumerate(values):
                    result_text += f"Row {i + 1}: {row}\n"

                return ToolActionResult(content=[{"type": "text", "text": result_text}])

            except HttpError as error:
                return ToolActionResult(
                    content=[{"type": "text", "text": f"Error reading range: {error}"}]
                )

        return ToolResult(
            code=[f"# Reading range: {params['range_name']}"],
            action=action,
            capture_snapshot=False,
            wait_for_network=False,
        )

    schema = ToolSchema(
        name="sheets_read_range",
        title="Read Range",
        description="Read data from a specific range in a Google Sheet",
        input_schema=ReadRangeInput,
        tool_type=ToolType.READ_ONLY,
    )

    return Tool(
        capability=ToolCapability.GOOGLE_SHEETS,
        schema=schema,
        handle=handle,
        browser_independent=True,
    )


@define_tool_factory(
    capability=ToolCapability.GOOGLE_SHEETS,
    name="sheets_write_range",
    title="Write Range",
    description="Write data to a specific range in a Google Sheet",
    input_schema=WriteRangeInput,
    tool_type=ToolType.DESTRUCTIVE,
)
def sheets_write_range_factory(capture_snapshot: bool) -> Tool:
    async def handle(context, params: Dict[str, Any]) -> ToolResult:
        async def action() -> ToolActionResult:
            try:
                service = get_google_sheets_service()

                body = {
                    "values": params["values"],
                    "majorDimension": params.get("major_dimension", "ROWS"),
                }

                result = (
                    service.spreadsheets()
                    .values()
                    .update(
                        spreadsheetId=params["spreadsheet_id"],
                        range=params["range_name"],
                        valueInputOption="RAW",
                        body=body,
                    )
                    .execute()
                )

                updated_cells = result.get("updatedCells", 0)

                return ToolActionResult(
                    content=[
                        {
                            "type": "text",
                            "text": f"Updated {updated_cells} cells in range: {params['range_name']}",
                        }
                    ]
                )

            except HttpError as error:
                return ToolActionResult(
                    content=[
                        {"type": "text", "text": f"Error writing to range: {error}"}
                    ]
                )

        return ToolResult(
            code=[f"# Writing to range: {params['range_name']}"],
            action=action,
            capture_snapshot=False,
            wait_for_network=False,
        )

    schema = ToolSchema(
        name="sheets_write_range",
        title="Write Range",
        description="Write data to a specific range in a Google Sheet",
        input_schema=WriteRangeInput,
        tool_type=ToolType.DESTRUCTIVE,
    )

    return Tool(
        capability=ToolCapability.GOOGLE_SHEETS,
        schema=schema,
        handle=handle,
        browser_independent=True,
    )


@define_tool_factory(
    capability=ToolCapability.GOOGLE_SHEETS,
    name="sheets_append_data",
    title="Append Data",
    description="Append data to the end of a Google Sheet",
    input_schema=AppendDataInput,
    tool_type=ToolType.DESTRUCTIVE,
)
def sheets_append_data_factory(capture_snapshot: bool) -> Tool:
    async def handle(context, params: Dict[str, Any]) -> ToolResult:
        async def action() -> ToolActionResult:
            try:
                service = get_google_sheets_service()

                body = {"values": params["values"]}

                result = (
                    service.spreadsheets()
                    .values()
                    .append(
                        spreadsheetId=params["spreadsheet_id"],
                        range=params["range_name"],
                        valueInputOption=params.get("value_input_option", "RAW"),
                        body=body,
                    )
                    .execute()
                )

                updated_cells = result.get("updates", {}).get("updatedCells", 0)

                return ToolActionResult(
                    content=[
                        {
                            "type": "text",
                            "text": f"Appended {updated_cells} cells to: {params['range_name']}",
                        }
                    ]
                )

            except HttpError as error:
                return ToolActionResult(
                    content=[{"type": "text", "text": f"Error appending data: {error}"}]
                )

        return ToolResult(
            code=[f"# Appending data to: {params['range_name']}"],
            action=action,
            capture_snapshot=False,
            wait_for_network=False,
        )

    schema = ToolSchema(
        name="sheets_append_data",
        title="Append Data",
        description="Append data to the end of a Google Sheet",
        input_schema=AppendDataInput,
        tool_type=ToolType.DESTRUCTIVE,
    )

    return Tool(
        capability=ToolCapability.GOOGLE_SHEETS,
        schema=schema,
        handle=handle,
        browser_independent=True,
    )


@define_tool_factory(
    capability=ToolCapability.GOOGLE_SHEETS,
    name="sheets_clear_range",
    title="Clear Range",
    description="Clear data from a specific range in a Google Sheet",
    input_schema=ClearRangeInput,
    tool_type=ToolType.DESTRUCTIVE,
)
def sheets_clear_range_factory(capture_snapshot: bool) -> Tool:
    async def handle(context, params: Dict[str, Any]) -> ToolResult:
        async def action() -> ToolActionResult:
            try:
                service = get_google_sheets_service()

                result = (
                    service.spreadsheets()
                    .values()
                    .clear(
                        spreadsheetId=params["spreadsheet_id"],
                        range=params["range_name"],
                    )
                    .execute()
                )

                return ToolActionResult(
                    content=[
                        {
                            "type": "text",
                            "text": f"Cleared range: {params['range_name']}",
                        }
                    ]
                )

            except HttpError as error:
                return ToolActionResult(
                    content=[{"type": "text", "text": f"Error clearing range: {error}"}]
                )

        return ToolResult(
            code=[f"# Clearing range: {params['range_name']}"],
            action=action,
            capture_snapshot=False,
            wait_for_network=False,
        )

    schema = ToolSchema(
        name="sheets_clear_range",
        title="Clear Range",
        description="Clear data from a specific range in a Google Sheet",
        input_schema=ClearRangeInput,
        tool_type=ToolType.DESTRUCTIVE,
    )

    return Tool(
        capability=ToolCapability.GOOGLE_SHEETS,
        schema=schema,
        handle=handle,
        browser_independent=True,
    )


def get_google_sheets_tools(capture_snapshot: bool = False) -> list[Tool]:
    return [
        sheets_create_spreadsheet_factory(capture_snapshot),
        sheets_open_spreadsheet_factory(capture_snapshot),
        sheets_share_spreadsheet_factory(capture_snapshot),
        sheets_list_spreadsheets_factory(capture_snapshot),
        sheets_create_worksheet_factory(capture_snapshot),
        sheets_read_range_factory(capture_snapshot),
        sheets_write_range_factory(capture_snapshot),
        sheets_append_data_factory(capture_snapshot),
        sheets_clear_range_factory(capture_snapshot),
    ]


GOOGLE_SHEETS_TOOLS = get_google_sheets_tools()
