import io
import csv
import pandas as pd
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload

from .tool_schema import (
    ToolInputSchema,
    ToolResult,
    ToolActionResult,
    define_tool,
    ToolCapability,
    ToolType,
)
from .google_sheets import get_google_sheets_service, get_google_drive_service


class ExportSheetInput(ToolInputSchema):
    spreadsheet_id: str = Field(description="Spreadsheet ID")
    format: str = Field(description="Export format: csv, pdf, xlsx, ods")
    sheet_id: Optional[int] = Field(default=None, description="Sheet ID to export (first sheet if None)")
    output_file: str = Field(description="Output file path")


class ImportCsvInput(ToolInputSchema):
    spreadsheet_id: str = Field(description="Spreadsheet ID")
    csv_file: str = Field(description="Path to CSV file to import")
    sheet_name: Optional[str] = Field(default=None, description="Sheet name to import to")
    range_name: Optional[str] = Field(default="A1", description="Starting range for import")
    clear_existing: Optional[bool] = Field(default=False, description="Clear existing data before import")


class ExportRangeInput(ToolInputSchema):
    spreadsheet_id: str = Field(description="Spreadsheet ID")
    range_name: str = Field(description="Range to export")
    format: str = Field(description="Export format: csv, json")
    output_file: str = Field(description="Output file path")


class CreateFromCsvInput(ToolInputSchema):
    csv_file: str = Field(description="Path to CSV file")
    spreadsheet_title: str = Field(description="Title for new spreadsheet")
    sheet_name: Optional[str] = Field(default="Sheet1", description="Name for the sheet")


class BackupSpreadsheetInput(ToolInputSchema):
    spreadsheet_id: str = Field(description="Spreadsheet ID to backup")
    backup_dir: str = Field(description="Directory to save backup files")
    include_metadata: Optional[bool] = Field(default=True, description="Include metadata in backup")


class RestoreSpreadsheetInput(ToolInputSchema):
    backup_file: str = Field(description="Path to backup file")
    new_title: Optional[str] = Field(default=None, description="Title for restored spreadsheet")


@define_tool(
    ToolCapability.GOOGLE_SHEETS,
    "sheets_export_sheet",
    "Export Sheet",
    "Export a Google Sheet to various formats (CSV, PDF, Excel)",
    ExportSheetInput,
    ToolType.READ_ONLY,
)
async def sheets_export_sheet(context, params: Dict[str, Any]) -> ToolResult:
    async def action() -> ToolActionResult:
        try:
            drive_service = get_google_drive_service()
            
            format_map = {
                'csv': 'text/csv',
                'pdf': 'application/pdf',
                'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'ods': 'application/vnd.oasis.opendocument.spreadsheet'
            }
            
            export_format = params['format'].lower()
            if export_format not in format_map:
                return ToolActionResult(content=[{
                    "type": "text",
                    "text": f"Unsupported format: {export_format}. Supported: {', '.join(format_map.keys())}"
                }])
            
            mime_type = format_map[export_format]
            
            export_params = {}
            if params.get('sheet_id') is not None:
                export_params['gid'] = params['sheet_id']
            
            request = drive_service.files().export_media(
                fileId=params['spreadsheet_id'],
                mimeType=mime_type,
                **export_params
            )
            
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            
            with open(params['output_file'], 'wb') as f:
                f.write(fh.getvalue())
            
            return ToolActionResult(content=[{
                "type": "text",
                "text": f"Exported sheet to {params['output_file']} in {export_format.upper()} format"
            }])
            
        except HttpError as error:
            return ToolActionResult(content=[{
                "type": "text",
                "text": f"Error exporting sheet: {error}"
            }])
        except Exception as error:
            return ToolActionResult(content=[{
                "type": "text",
                "text": f"Error saving file: {error}"
            }])
    
    return ToolResult(
        code=[f"# Exporting sheet to {params['format'].upper()} format"],
        action=action,
        result_override=None
    )


@define_tool(
    ToolCapability.GOOGLE_SHEETS,
    "sheets_import_csv",
    "Import CSV",
    "Import CSV data into a Google Sheet",
    ImportCsvInput,
    ToolType.DESTRUCTIVE,
)
async def sheets_import_csv(context, params: Dict[str, Any]) -> ToolResult:
    async def action() -> ToolActionResult:
        try:
            service = get_google_sheets_service()
            
            with open(params['csv_file'], 'r', encoding='utf-8') as f:
                csv_reader = csv.reader(f)
                values = list(csv_reader)
            
            if not values:
                return ToolActionResult(content=[{
                    "type": "text",
                    "text": "CSV file is empty"
                }])
            
            range_name = params.get('range_name', 'A1')
            if params.get('sheet_name'):
                range_name = f"{params['sheet_name']}!{range_name}"
            
            if params.get('clear_existing', False):
                service.spreadsheets().values().clear(
                    spreadsheetId=params['spreadsheet_id'],
                    range=range_name.split('!')[0] if '!' in range_name else 'Sheet1'
                ).execute()
            
            body = {
                'values': values,
                'majorDimension': 'ROWS'
            }
            
            result = service.spreadsheets().values().update(
                spreadsheetId=params['spreadsheet_id'],
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            updated_cells = result.get('updatedCells', 0)
            
            return ToolActionResult(content=[{
                "type": "text",
                "text": f"Imported CSV data: {updated_cells} cells updated from {params['csv_file']}"
            }])
            
        except FileNotFoundError:
            return ToolActionResult(content=[{
                "type": "text",
                "text": f"CSV file not found: {params['csv_file']}"
            }])
        except HttpError as error:
            return ToolActionResult(content=[{
                "type": "text",
                "text": f"Error importing CSV: {error}"
            }])
        except Exception as error:
            return ToolActionResult(content=[{
                "type": "text",
                "text": f"Error reading CSV file: {error}"
            }])
    
    return ToolResult(
        code=[f"# Importing CSV from {params['csv_file']}"],
        action=action,
        result_override=None
    )


@define_tool(
    ToolCapability.GOOGLE_SHEETS,
    "sheets_export_range",
    "Export Range",
    "Export a specific range from Google Sheet to CSV or JSON",
    ExportRangeInput,
    ToolType.READ_ONLY,
)
async def sheets_export_range(context, params: Dict[str, Any]) -> ToolResult:
    async def action() -> ToolActionResult:
        try:
            service = get_google_sheets_service()
            
            result = service.spreadsheets().values().get(
                spreadsheetId=params['spreadsheet_id'],
                range=params['range_name'],
                majorDimension='ROWS'
            ).execute()
            
            values = result.get('values', [])
            
            if not values:
                return ToolActionResult(content=[{
                    "type": "text",
                    "text": f"No data found in range: {params['range_name']}"
                }])
            
            export_format = params['format'].lower()
            
            if export_format == 'csv':
                with open(params['output_file'], 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    for row in values:
                        writer.writerow(row)
            
            elif export_format == 'json':
                import json
                
                if len(values) > 1:
                    headers = values[0]
                    data = []
                    for row in values[1:]:
                        row_dict = {}
                        for i, header in enumerate(headers):
                            value = row[i] if i < len(row) else ""
                            row_dict[header] = value
                        data.append(row_dict)
                else:
                    data = values
                
                with open(params['output_file'], 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            
            else:
                return ToolActionResult(content=[{
                    "type": "text",
                    "text": f"Unsupported format: {export_format}. Supported: csv, json"
                }])
            
            return ToolActionResult(content=[{
                "type": "text",
                "text": f"Exported range {params['range_name']} to {params['output_file']} in {export_format.upper()} format"
            }])
            
        except HttpError as error:
            return ToolActionResult(content=[{
                "type": "text",
                "text": f"Error exporting range: {error}"
            }])
        except Exception as error:
            return ToolActionResult(content=[{
                "type": "text",
                "text": f"Error saving file: {error}"
            }])
    
    return ToolResult(
        code=[f"# Exporting range {params['range_name']} to {params['format'].upper()}"],
        action=action,
        result_override=None
    )


@define_tool(
    ToolCapability.GOOGLE_SHEETS,
    "sheets_create_from_csv",
    "Create from CSV",
    "Create a new Google Spreadsheet from a CSV file",
    CreateFromCsvInput,
    ToolType.DESTRUCTIVE,
)
async def sheets_create_from_csv(context, params: Dict[str, Any]) -> ToolResult:
    async def action() -> ToolActionResult:
        try:
            sheets_service = get_google_sheets_service()
            
            with open(params['csv_file'], 'r', encoding='utf-8') as f:
                csv_reader = csv.reader(f)
                values = list(csv_reader)
            
            if not values:
                return ToolActionResult(content=[{
                    "type": "text",
                    "text": "CSV file is empty"
                }])
            
            spreadsheet_body = {
                'properties': {
                    'title': params['spreadsheet_title']
                },
                'sheets': [{
                    'properties': {
                        'title': params.get('sheet_name', 'Sheet1'),
                        'gridProperties': {
                            'rowCount': len(values) + 100,
                            'columnCount': max(len(row) for row in values) + 10
                        }
                    }
                }]
            }
            
            spreadsheet = sheets_service.spreadsheets().create(
                body=spreadsheet_body
            ).execute()
            
            spreadsheet_id = spreadsheet.get('spreadsheetId')
            
            body = {
                'values': values,
                'majorDimension': 'ROWS'
            }
            
            range_name = f"{params.get('sheet_name', 'Sheet1')}!A1"
            
            sheets_service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            
            spreadsheet_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
            
            return ToolActionResult(content=[{
                "type": "text",
                "text": f"Created spreadsheet from CSV: {params['spreadsheet_title']}\nID: {spreadsheet_id}\nURL: {spreadsheet_url}\nImported {len(values)} rows"
            }])
            
        except FileNotFoundError:
            return ToolActionResult(content=[{
                "type": "text",
                "text": f"CSV file not found: {params['csv_file']}"
            }])
        except HttpError as error:
            return ToolActionResult(content=[{
                "type": "text",
                "text": f"Error creating spreadsheet: {error}"
            }])
        except Exception as error:
            return ToolActionResult(content=[{
                "type": "text",
                "text": f"Error reading CSV file: {error}"
            }])
    
    return ToolResult(
        code=[f"# Creating spreadsheet from CSV: {params['csv_file']}"],
        action=action,
        result_override=None
    )


@define_tool(
    ToolCapability.GOOGLE_SHEETS,
    "sheets_backup_spreadsheet",
    "Backup Spreadsheet",
    "Create a complete backup of a Google Spreadsheet",
    BackupSpreadsheetInput,
    ToolType.READ_ONLY,
)
async def sheets_backup_spreadsheet(context, params: Dict[str, Any]) -> ToolResult:
    async def action() -> ToolActionResult:
        try:
            import os
            import json
            from datetime import datetime
            
            sheets_service = get_google_sheets_service()
            drive_service = get_google_drive_service()
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = params['backup_dir']
            
            os.makedirs(backup_dir, exist_ok=True)
            
            spreadsheet = sheets_service.spreadsheets().get(
                spreadsheetId=params['spreadsheet_id']
            ).execute()
            
            title = spreadsheet.get('properties', {}).get('title', 'Unknown')
            safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            
            if params.get('include_metadata', True):
                metadata_file = os.path.join(backup_dir, f"{safe_title}_metadata_{timestamp}.json")
                with open(metadata_file, 'w', encoding='utf-8') as f:
                    json.dump(spreadsheet, f, indent=2, ensure_ascii=False)
            
            backup_files = []
            
            for sheet in spreadsheet.get('sheets', []):
                sheet_props = sheet.get('properties', {})
                sheet_title = sheet_props.get('title', 'Unknown')
                sheet_id = sheet_props.get('sheetId', 0)
                
                safe_sheet_title = "".join(c for c in sheet_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                
                csv_file = os.path.join(backup_dir, f"{safe_title}_{safe_sheet_title}_{timestamp}.csv")
                
                request = drive_service.files().export_media(
                    fileId=params['spreadsheet_id'],
                    mimeType='text/csv',
                    gid=sheet_id
                )
                
                fh = io.BytesIO()
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
                
                with open(csv_file, 'wb') as f:
                    f.write(fh.getvalue())
                
                backup_files.append(csv_file)
            
            xlsx_file = os.path.join(backup_dir, f"{safe_title}_{timestamp}.xlsx")
            
            request = drive_service.files().export_media(
                fileId=params['spreadsheet_id'],
                mimeType='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            
            with open(xlsx_file, 'wb') as f:
                f.write(fh.getvalue())
            
            backup_files.append(xlsx_file)
            
            result_text = f"Backup completed for spreadsheet: {title}\n"
            result_text += f"Backup directory: {backup_dir}\n"
            result_text += f"Files created:\n"
            for file in backup_files:
                result_text += f"- {os.path.basename(file)}\n"
            if params.get('include_metadata', True):
                result_text += f"- {os.path.basename(metadata_file)}\n"
            
            return ToolActionResult(content=[{
                "type": "text",
                "text": result_text
            }])
            
        except HttpError as error:
            return ToolActionResult(content=[{
                "type": "text",
                "text": f"Error backing up spreadsheet: {error}"
            }])
        except Exception as error:
            return ToolActionResult(content=[{
                "type": "text",
                "text": f"Error creating backup: {error}"
            }])
    
    return ToolResult(
        code=[f"# Creating backup of spreadsheet"],
        action=action,
        result_override=None
    )


GOOGLE_SHEETS_EXPORT_TOOLS = [
    sheets_export_sheet,
    sheets_import_csv,
    sheets_export_range,
    sheets_create_from_csv,
    sheets_backup_spreadsheet,
] 