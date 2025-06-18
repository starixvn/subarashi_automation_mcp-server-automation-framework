from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from googleapiclient.errors import HttpError

from .tool_schema import (
    ToolInputSchema,
    ToolResult,
    ToolActionResult,
    define_tool,
    ToolCapability,
    ToolType,
)
from .google_sheets import get_google_sheets_service


class FormatCellsInput(ToolInputSchema):
    spreadsheet_id: str = Field(description="Spreadsheet ID")
    range_name: str = Field(description="Range to format")
    bold: Optional[bool] = Field(default=None, description="Make text bold")
    italic: Optional[bool] = Field(default=None, description="Make text italic")
    font_size: Optional[int] = Field(default=None, description="Font size")
    background_color: Optional[Dict[str, float]] = Field(default=None, description="Background color RGB (0-1)")
    text_color: Optional[Dict[str, float]] = Field(default=None, description="Text color RGB (0-1)")


class MergeCellsInput(ToolInputSchema):
    spreadsheet_id: str = Field(description="Spreadsheet ID")
    range_name: str = Field(description="Range to merge")
    merge_type: Optional[str] = Field(default="MERGE_ALL", description="MERGE_ALL, MERGE_COLUMNS, MERGE_ROWS")


class SortRangeInput(ToolInputSchema):
    spreadsheet_id: str = Field(description="Spreadsheet ID")
    range_name: str = Field(description="Range to sort")
    sort_column: int = Field(description="Column index to sort by (0-based)")
    ascending: Optional[bool] = Field(default=True, description="Sort in ascending order")


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
    sheet_id: Optional[int] = Field(default=None, description="Sheet ID to search in (all sheets if None)")
    match_case: Optional[bool] = Field(default=False, description="Match case sensitivity")
    match_entire_cell: Optional[bool] = Field(default=False, description="Match entire cell content")


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


class DeleteWorksheetInput(ToolInputSchema):
    spreadsheet_id: str = Field(description="Spreadsheet ID")
    sheet_id: int = Field(description="Sheet ID to delete")


class RenameWorksheetInput(ToolInputSchema):
    spreadsheet_id: str = Field(description="Spreadsheet ID")
    sheet_id: int = Field(description="Sheet ID to rename")
    new_title: str = Field(description="New title for the worksheet")


class ListWorksheetsInput(ToolInputSchema):
    spreadsheet_id: str = Field(description="Spreadsheet ID")


class UpdateCellInput(ToolInputSchema):
    spreadsheet_id: str = Field(description="Spreadsheet ID")
    range_name: str = Field(description="Single cell range (e.g., 'Sheet1!A1')")
    value: Any = Field(description="Value to write to the cell")


def parse_range_to_grid_range(range_name: str, sheet_id: int = 0) -> Dict[str, Any]:
    if '!' in range_name:
        sheet_part, range_part = range_name.split('!', 1)
    else:
        range_part = range_name
    
    if ':' in range_part:
        start_cell, end_cell = range_part.split(':', 1)
    else:
        start_cell = end_cell = range_part
    
    def cell_to_indices(cell: str):
        col = 0
        row = 0
        i = 0
        while i < len(cell) and cell[i].isalpha():
            col = col * 26 + (ord(cell[i].upper()) - ord('A') + 1)
            i += 1
        col -= 1
        if i < len(cell):
            row = int(cell[i:]) - 1
        return row, col
    
    start_row, start_col = cell_to_indices(start_cell)
    end_row, end_col = cell_to_indices(end_cell)
    
    return {
        'sheetId': sheet_id,
        'startRowIndex': start_row,
        'endRowIndex': end_row + 1,
        'startColumnIndex': start_col,
        'endColumnIndex': end_col + 1
    }


@define_tool(
    ToolCapability.GOOGLE_SHEETS,
    "sheets_format_cells",
    "Format Cells",
    "Format cells in a Google Sheet (bold, italic, colors, etc.)",
    FormatCellsInput,
    ToolType.DESTRUCTIVE,
)
async def sheets_format_cells(context, params: Dict[str, Any]) -> ToolResult:
    async def action() -> ToolActionResult:
        try:
            service = get_google_sheets_service()
            
            requests = []
            
            text_format = {}
            if params.get('bold') is not None:
                text_format['bold'] = params['bold']
            if params.get('italic') is not None:
                text_format['italic'] = params['italic']
            if params.get('font_size') is not None:
                text_format['fontSize'] = params['font_size']
            
            cell_format = {}
            if text_format:
                cell_format['textFormat'] = text_format
            
            if params.get('background_color'):
                cell_format['backgroundColor'] = params['background_color']
            
            if params.get('text_color'):
                if 'textFormat' not in cell_format:
                    cell_format['textFormat'] = {}
                cell_format['textFormat']['foregroundColor'] = params['text_color']
            
            if cell_format:
                grid_range = parse_range_to_grid_range(params['range_name'])
                
                requests.append({
                    'repeatCell': {
                        'range': grid_range,
                        'cell': {
                            'userEnteredFormat': cell_format
                        },
                        'fields': 'userEnteredFormat'
                    }
                })
            
            if requests:
                body = {'requests': requests}
                service.spreadsheets().batchUpdate(
                    spreadsheetId=params['spreadsheet_id'],
                    body=body
                ).execute()
            
            return ToolActionResult(content=[{
                "type": "text",
                "text": f"Formatted cells in range: {params['range_name']}"
            }])
            
        except HttpError as error:
            return ToolActionResult(content=[{
                "type": "text",
                "text": f"Error formatting cells: {error}"
            }])
    
    return ToolResult(
        code=[f"# Formatting cells in range: {params['range_name']}"],
        action=action,
        result_override=None
    )


@define_tool(
    ToolCapability.GOOGLE_SHEETS,
    "sheets_merge_cells",
    "Merge Cells",
    "Merge cells in a Google Sheet",
    MergeCellsInput,
    ToolType.DESTRUCTIVE,
)
async def sheets_merge_cells(context, params: Dict[str, Any]) -> ToolResult:
    async def action() -> ToolActionResult:
        try:
            service = get_google_sheets_service()
            
            grid_range = parse_range_to_grid_range(params['range_name'])
            
            request = {
                'mergeCells': {
                    'range': grid_range,
                    'mergeType': params.get('merge_type', 'MERGE_ALL')
                }
            }
            
            body = {'requests': [request]}
            
            service.spreadsheets().batchUpdate(
                spreadsheetId=params['spreadsheet_id'],
                body=body
            ).execute()
            
            return ToolActionResult(content=[{
                "type": "text",
                "text": f"Merged cells in range: {params['range_name']}"
            }])
            
        except HttpError as error:
            return ToolActionResult(content=[{
                "type": "text",
                "text": f"Error merging cells: {error}"
            }])
    
    return ToolResult(
        code=[f"# Merging cells in range: {params['range_name']}"],
        action=action,
        result_override=None
    )


@define_tool(
    ToolCapability.GOOGLE_SHEETS,
    "sheets_sort_range",
    "Sort Range",
    "Sort data in a Google Sheet range",
    SortRangeInput,
    ToolType.DESTRUCTIVE,
)
async def sheets_sort_range(context, params: Dict[str, Any]) -> ToolResult:
    async def action() -> ToolActionResult:
        try:
            service = get_google_sheets_service()
            
            grid_range = parse_range_to_grid_range(params['range_name'])
            
            request = {
                'sortRange': {
                    'range': grid_range,
                    'sortSpecs': [{
                        'dimensionIndex': params['sort_column'],
                        'sortOrder': 'ASCENDING' if params.get('ascending', True) else 'DESCENDING'
                    }]
                }
            }
            
            body = {'requests': [request]}
            
            service.spreadsheets().batchUpdate(
                spreadsheetId=params['spreadsheet_id'],
                body=body
            ).execute()
            
            order = "ascending" if params.get('ascending', True) else "descending"
            return ToolActionResult(content=[{
                "type": "text",
                "text": f"Sorted range {params['range_name']} by column {params['sort_column']} in {order} order"
            }])
            
        except HttpError as error:
            return ToolActionResult(content=[{
                "type": "text",
                "text": f"Error sorting range: {error}"
            }])
    
    return ToolResult(
        code=[f"# Sorting range: {params['range_name']}"],
        action=action,
        result_override=None
    )


@define_tool(
    ToolCapability.GOOGLE_SHEETS,
    "sheets_insert_rows",
    "Insert Rows",
    "Insert rows in a Google Sheet",
    InsertRowsInput,
    ToolType.DESTRUCTIVE,
)
async def sheets_insert_rows(context, params: Dict[str, Any]) -> ToolResult:
    async def action() -> ToolActionResult:
        try:
            service = get_google_sheets_service()
            
            request = {
                'insertDimension': {
                    'range': {
                        'sheetId': params['sheet_id'],
                        'dimension': 'ROWS',
                        'startIndex': params['start_index'],
                        'endIndex': params['end_index']
                    },
                    'inheritFromBefore': False
                }
            }
            
            body = {'requests': [request]}
            
            service.spreadsheets().batchUpdate(
                spreadsheetId=params['spreadsheet_id'],
                body=body
            ).execute()
            
            row_count = params['end_index'] - params['start_index']
            return ToolActionResult(content=[{
                "type": "text",
                "text": f"Inserted {row_count} rows starting at index {params['start_index']}"
            }])
            
        except HttpError as error:
            return ToolActionResult(content=[{
                "type": "text",
                "text": f"Error inserting rows: {error}"
            }])
    
    return ToolResult(
        code=[f"# Inserting rows at index {params['start_index']}"],
        action=action,
        result_override=None
    )


@define_tool(
    ToolCapability.GOOGLE_SHEETS,
    "sheets_insert_columns",
    "Insert Columns",
    "Insert columns in a Google Sheet",
    InsertColumnsInput,
    ToolType.DESTRUCTIVE,
)
async def sheets_insert_columns(context, params: Dict[str, Any]) -> ToolResult:
    async def action() -> ToolActionResult:
        try:
            service = get_google_sheets_service()
            
            request = {
                'insertDimension': {
                    'range': {
                        'sheetId': params['sheet_id'],
                        'dimension': 'COLUMNS',
                        'startIndex': params['start_index'],
                        'endIndex': params['end_index']
                    },
                    'inheritFromBefore': False
                }
            }
            
            body = {'requests': [request]}
            
            service.spreadsheets().batchUpdate(
                spreadsheetId=params['spreadsheet_id'],
                body=body
            ).execute()
            
            column_count = params['end_index'] - params['start_index']
            return ToolActionResult(content=[{
                "type": "text",
                "text": f"Inserted {column_count} columns starting at index {params['start_index']}"
            }])
            
        except HttpError as error:
            return ToolActionResult(content=[{
                "type": "text",
                "text": f"Error inserting columns: {error}"
            }])
    
    return ToolResult(
        code=[f"# Inserting columns at index {params['start_index']}"],
        action=action,
        result_override=None
    )


@define_tool(
    ToolCapability.GOOGLE_SHEETS,
    "sheets_delete_rows",
    "Delete Rows",
    "Delete rows in a Google Sheet",
    DeleteRowsInput,
    ToolType.DESTRUCTIVE,
)
async def sheets_delete_rows(context, params: Dict[str, Any]) -> ToolResult:
    async def action() -> ToolActionResult:
        try:
            service = get_google_sheets_service()
            
            request = {
                'deleteDimension': {
                    'range': {
                        'sheetId': params['sheet_id'],
                        'dimension': 'ROWS',
                        'startIndex': params['start_index'],
                        'endIndex': params['end_index']
                    }
                }
            }
            
            body = {'requests': [request]}
            
            service.spreadsheets().batchUpdate(
                spreadsheetId=params['spreadsheet_id'],
                body=body
            ).execute()
            
            row_count = params['end_index'] - params['start_index']
            return ToolActionResult(content=[{
                "type": "text",
                "text": f"Deleted {row_count} rows starting at index {params['start_index']}"
            }])
            
        except HttpError as error:
            return ToolActionResult(content=[{
                "type": "text",
                "text": f"Error deleting rows: {error}"
            }])
    
    return ToolResult(
        code=[f"# Deleting rows at index {params['start_index']}"],
        action=action,
        result_override=None
    )


@define_tool(
    ToolCapability.GOOGLE_SHEETS,
    "sheets_delete_columns",
    "Delete Columns",
    "Delete columns in a Google Sheet",
    DeleteColumnsInput,
    ToolType.DESTRUCTIVE,
)
async def sheets_delete_columns(context, params: Dict[str, Any]) -> ToolResult:
    async def action() -> ToolActionResult:
        try:
            service = get_google_sheets_service()
            
            request = {
                'deleteDimension': {
                    'range': {
                        'sheetId': params['sheet_id'],
                        'dimension': 'COLUMNS',
                        'startIndex': params['start_index'],
                        'endIndex': params['end_index']
                    }
                }
            }
            
            body = {'requests': [request]}
            
            service.spreadsheets().batchUpdate(
                spreadsheetId=params['spreadsheet_id'],
                body=body
            ).execute()
            
            column_count = params['end_index'] - params['start_index']
            return ToolActionResult(content=[{
                "type": "text",
                "text": f"Deleted {column_count} columns starting at index {params['start_index']}"
            }])
            
        except HttpError as error:
            return ToolActionResult(content=[{
                "type": "text",
                "text": f"Error deleting columns: {error}"
            }])
    
    return ToolResult(
        code=[f"# Deleting columns at index {params['start_index']}"],
        action=action,
        result_override=None
    )


@define_tool(
    ToolCapability.GOOGLE_SHEETS,
    "sheets_find_replace",
    "Find and Replace",
    "Find and replace text in a Google Sheet",
    FindReplaceInput,
    ToolType.DESTRUCTIVE,
)
async def sheets_find_replace(context, params: Dict[str, Any]) -> ToolResult:
    async def action() -> ToolActionResult:
        try:
            service = get_google_sheets_service()
            
            request = {
                'findReplace': {
                    'find': params['find_text'],
                    'replacement': params['replace_text'],
                    'matchCase': params.get('match_case', False),
                    'matchEntireCell': params.get('match_entire_cell', False),
                    'searchByRegex': False,
                    'includeFormulas': True
                }
            }
            
            if params.get('sheet_id') is not None:
                request['findReplace']['range'] = {
                    'sheetId': params['sheet_id']
                }
            
            body = {'requests': [request]}
            
            response = service.spreadsheets().batchUpdate(
                spreadsheetId=params['spreadsheet_id'],
                body=body
            ).execute()
            
            occurrences_changed = response['replies'][0]['findReplace']['occurrencesChanged']
            
            return ToolActionResult(content=[{
                "type": "text",
                "text": f"Replaced {occurrences_changed} occurrences of '{params['find_text']}' with '{params['replace_text']}'"
            }])
            
        except HttpError as error:
            return ToolActionResult(content=[{
                "type": "text",
                "text": f"Error in find and replace: {error}"
            }])
    
    return ToolResult(
        code=[f"# Finding and replacing '{params['find_text']}' with '{params['replace_text']}'"],
        action=action,
        result_override=None
    )


@define_tool(
    ToolCapability.GOOGLE_SHEETS,
    "sheets_add_formula",
    "Add Formula",
    "Add a formula to a cell in a Google Sheet",
    AddFormulaInput,
    ToolType.DESTRUCTIVE,
)
async def sheets_add_formula(context, params: Dict[str, Any]) -> ToolResult:
    async def action() -> ToolActionResult:
        try:
            service = get_google_sheets_service()
            
            formula = f"={params['formula']}"
            
            body = {
                'values': [[formula]],
                'majorDimension': 'ROWS'
            }
            
            result = service.spreadsheets().values().update(
                spreadsheetId=params['spreadsheet_id'],
                range=params['range_name'],
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            
            return ToolActionResult(content=[{
                "type": "text",
                "text": f"Added formula '{formula}' to range: {params['range_name']}"
            }])
            
        except HttpError as error:
            return ToolActionResult(content=[{
                "type": "text",
                "text": f"Error adding formula: {error}"
            }])
    
    return ToolResult(
        code=[f"# Adding formula to range: {params['range_name']}"],
        action=action,
        result_override=None
    )


@define_tool(
    ToolCapability.GOOGLE_SHEETS,
    "sheets_freeze_rows",
    "Freeze Rows",
    "Freeze rows in a Google Sheet",
    FreezeRowsInput,
    ToolType.DESTRUCTIVE,
)
async def sheets_freeze_rows(context, params: Dict[str, Any]) -> ToolResult:
    async def action() -> ToolActionResult:
        try:
            service = get_google_sheets_service()
            
            request = {
                'updateSheetProperties': {
                    'properties': {
                        'sheetId': params['sheet_id'],
                        'gridProperties': {
                            'frozenRowCount': params['frozen_row_count']
                        }
                    },
                    'fields': 'gridProperties.frozenRowCount'
                }
            }
            
            body = {'requests': [request]}
            
            service.spreadsheets().batchUpdate(
                spreadsheetId=params['spreadsheet_id'],
                body=body
            ).execute()
            
            return ToolActionResult(content=[{
                "type": "text",
                "text": f"Froze {params['frozen_row_count']} rows"
            }])
            
        except HttpError as error:
            return ToolActionResult(content=[{
                "type": "text",
                "text": f"Error freezing rows: {error}"
            }])
    
    return ToolResult(
        code=[f"# Freezing {params['frozen_row_count']} rows"],
        action=action,
        result_override=None
    )


@define_tool(
    ToolCapability.GOOGLE_SHEETS,
    "sheets_freeze_columns",
    "Freeze Columns",
    "Freeze columns in a Google Sheet",
    FreezeColumnsInput,
    ToolType.DESTRUCTIVE,
)
async def sheets_freeze_columns(context, params: Dict[str, Any]) -> ToolResult:
    async def action() -> ToolActionResult:
        try:
            service = get_google_sheets_service()
            
            request = {
                'updateSheetProperties': {
                    'properties': {
                        'sheetId': params['sheet_id'],
                        'gridProperties': {
                            'frozenColumnCount': params['frozen_column_count']
                        }
                    },
                    'fields': 'gridProperties.frozenColumnCount'
                }
            }
            
            body = {'requests': [request]}
            
            service.spreadsheets().batchUpdate(
                spreadsheetId=params['spreadsheet_id'],
                body=body
            ).execute()
            
            return ToolActionResult(content=[{
                "type": "text",
                "text": f"Froze {params['frozen_column_count']} columns"
            }])
            
        except HttpError as error:
            return ToolActionResult(content=[{
                "type": "text",
                "text": f"Error freezing columns: {error}"
            }])
    
    return ToolResult(
        code=[f"# Freezing {params['frozen_column_count']} columns"],
        action=action,
        result_override=None
    )


@define_tool(
    ToolCapability.GOOGLE_SHEETS,
    "sheets_delete_worksheet",
    "Delete Worksheet",
    "Delete a worksheet from a Google Spreadsheet",
    DeleteWorksheetInput,
    ToolType.DESTRUCTIVE,
)
async def sheets_delete_worksheet(context, params: Dict[str, Any]) -> ToolResult:
    async def action() -> ToolActionResult:
        try:
            service = get_google_sheets_service()
            
            request = {
                'deleteSheet': {
                    'sheetId': params['sheet_id']
                }
            }
            
            body = {'requests': [request]}
            
            service.spreadsheets().batchUpdate(
                spreadsheetId=params['spreadsheet_id'],
                body=body
            ).execute()
            
            return ToolActionResult(content=[{
                "type": "text",
                "text": f"Deleted worksheet with ID: {params['sheet_id']}"
            }])
            
        except HttpError as error:
            return ToolActionResult(content=[{
                "type": "text",
                "text": f"Error deleting worksheet: {error}"
            }])
    
    return ToolResult(
        code=[f"# Deleting worksheet with ID: {params['sheet_id']}"],
        action=action,
        result_override=None
    )


@define_tool(
    ToolCapability.GOOGLE_SHEETS,
    "sheets_rename_worksheet",
    "Rename Worksheet",
    "Rename a worksheet in a Google Spreadsheet",
    RenameWorksheetInput,
    ToolType.DESTRUCTIVE,
)
async def sheets_rename_worksheet(context, params: Dict[str, Any]) -> ToolResult:
    async def action() -> ToolActionResult:
        try:
            service = get_google_sheets_service()
            
            request = {
                'updateSheetProperties': {
                    'properties': {
                        'sheetId': params['sheet_id'],
                        'title': params['new_title']
                    },
                    'fields': 'title'
                }
            }
            
            body = {'requests': [request]}
            
            service.spreadsheets().batchUpdate(
                spreadsheetId=params['spreadsheet_id'],
                body=body
            ).execute()
            
            return ToolActionResult(content=[{
                "type": "text",
                "text": f"Renamed worksheet to: {params['new_title']}"
            }])
            
        except HttpError as error:
            return ToolActionResult(content=[{
                "type": "text",
                "text": f"Error renaming worksheet: {error}"
            }])
    
    return ToolResult(
        code=[f"# Renaming worksheet to: {params['new_title']}"],
        action=action,
        result_override=None
    )


@define_tool(
    ToolCapability.GOOGLE_SHEETS,
    "sheets_list_worksheets",
    "List Worksheets",
    "List all worksheets in a Google Spreadsheet",
    ListWorksheetsInput,
    ToolType.READ_ONLY,
)
async def sheets_list_worksheets(context, params: Dict[str, Any]) -> ToolResult:
    async def action() -> ToolActionResult:
        try:
            service = get_google_sheets_service()
            
            spreadsheet = service.spreadsheets().get(
                spreadsheetId=params['spreadsheet_id']
            ).execute()
            
            sheets = spreadsheet.get('sheets', [])
            
            if not sheets:
                return ToolActionResult(content=[{
                    "type": "text",
                    "text": "No worksheets found in the spreadsheet"
                }])
            
            result_text = "Worksheets in spreadsheet:\n"
            for sheet in sheets:
                properties = sheet.get('properties', {})
                title = properties.get('title', 'Unknown')
                sheet_id = properties.get('sheetId', 'Unknown')
                grid_props = properties.get('gridProperties', {})
                rows = grid_props.get('rowCount', 'Unknown')
                cols = grid_props.get('columnCount', 'Unknown')
                
                result_text += f"- {title} (ID: {sheet_id}, Size: {rows}x{cols})\n"
            
            return ToolActionResult(content=[{
                "type": "text",
                "text": result_text
            }])
            
        except HttpError as error:
            return ToolActionResult(content=[{
                "type": "text",
                "text": f"Error listing worksheets: {error}"
            }])
    
    return ToolResult(
        code=[f"# Listing worksheets"],
        action=action,
        result_override=None
    )


@define_tool(
    ToolCapability.GOOGLE_SHEETS,
    "sheets_update_cell",
    "Update Cell",
    "Update a single cell in a Google Sheet",
    UpdateCellInput,
    ToolType.DESTRUCTIVE,
)
async def sheets_update_cell(context, params: Dict[str, Any]) -> ToolResult:
    async def action() -> ToolActionResult:
        try:
            service = get_google_sheets_service()
            
            body = {
                'values': [[params['value']]],
                'majorDimension': 'ROWS'
            }
            
            result = service.spreadsheets().values().update(
                spreadsheetId=params['spreadsheet_id'],
                range=params['range_name'],
                valueInputOption='RAW',
                body=body
            ).execute()
            
            return ToolActionResult(content=[{
                "type": "text",
                "text": f"Updated cell {params['range_name']} with value: {params['value']}"
            }])
            
        except HttpError as error:
            return ToolActionResult(content=[{
                "type": "text",
                "text": f"Error updating cell: {error}"
            }])
    
    return ToolResult(
        code=[f"# Updating cell: {params['range_name']}"],
        action=action,
        result_override=None
    )


GOOGLE_SHEETS_ADVANCED_TOOLS = [
    sheets_format_cells,
    sheets_merge_cells,
    sheets_sort_range,
    sheets_insert_rows,
    sheets_insert_columns,
    sheets_delete_rows,
    sheets_delete_columns,
    sheets_find_replace,
    sheets_add_formula,
    sheets_freeze_rows,
    sheets_freeze_columns,
    sheets_delete_worksheet,
    sheets_rename_worksheet,
    sheets_list_worksheets,
    sheets_update_cell,
] 