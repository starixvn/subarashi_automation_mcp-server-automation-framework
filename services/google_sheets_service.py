import os
from typing import Any, List, Optional
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from .base_service import BaseService, ServiceResult

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

SERVICE_ACCOUNT_FILE = "config/keys/service-account.json"


def get_google_sheets_service():
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        raise FileNotFoundError(
            f"Service account file not found: {SERVICE_ACCOUNT_FILE}"
        )

    credentials = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    return build("sheets", "v4", credentials=credentials)


class GoogleSheetsService(BaseService):
    def __init__(self, context):
        super().__init__(context)

    async def create_spreadsheet(
        self, title: str, sheet_names: Optional[List[str]] = None
    ) -> ServiceResult:
        try:
            service = get_google_sheets_service()

            spreadsheet_body = {"properties": {"title": title}, "sheets": []}

            if sheet_names:
                for i, sheet_name in enumerate(sheet_names):
                    sheet = {
                        "properties": {
                            "sheetId": i,
                            "title": sheet_name,
                            "gridProperties": {"rowCount": 1000, "columnCount": 26},
                        }
                    }
                    spreadsheet_body["sheets"].append(sheet)

            result = service.spreadsheets().create(body=spreadsheet_body).execute()

            return ServiceResult(
                success=True,
                message=f"Created spreadsheet: {title}",
                data={
                    "spreadsheet_id": result["spreadsheetId"],
                    "spreadsheet_url": result["spreadsheetUrl"],
                    "title": title,
                },
            )

        except HttpError as error:
            return ServiceResult(
                success=False,
                message=f"Error creating spreadsheet: {error}",
                error=str(error),
            )
        except Exception as e:
            return ServiceResult(
                success=False,
                message=f"Failed to create spreadsheet: {str(e)}",
                error=str(e),
            )

    async def open_spreadsheet(
        self, spreadsheet_id: Optional[str] = None, url: Optional[str] = None
    ) -> ServiceResult:
        try:
            if url and not spreadsheet_id:
                if "/d/" in url:
                    spreadsheet_id = url.split("/d/")[1].split("/")[0]
                else:
                    return ServiceResult(
                        success=False,
                        message="Invalid Google Sheets URL format",
                        error="invalid_url",
                    )

            if not spreadsheet_id:
                return ServiceResult(
                    success=False,
                    message="Either spreadsheet_id or url must be provided",
                    error="missing_identifier",
                )

            service = get_google_sheets_service()
            result = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()

            return ServiceResult(
                success=True,
                message=f"Opened spreadsheet: {result['properties']['title']}",
                data={
                    "spreadsheet_id": spreadsheet_id,
                    "title": result["properties"]["title"],
                    "spreadsheet_url": f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit",
                },
            )

        except HttpError as error:
            return ServiceResult(
                success=False,
                message=f"Error opening spreadsheet: {error}",
                error=str(error),
            )
        except Exception as e:
            return ServiceResult(
                success=False,
                message=f"Failed to open spreadsheet: {str(e)}",
                error=str(e),
            )

    async def share_spreadsheet(
        self, spreadsheet_id: str, email: str, role: str = "writer"
    ) -> ServiceResult:
        try:
            drive_service = build(
                "drive",
                "v3",
                credentials=Credentials.from_service_account_file(
                    SERVICE_ACCOUNT_FILE, scopes=SCOPES
                ),
            )

            permission = {"type": "user", "role": role, "emailAddress": email}

            drive_service.permissions().create(
                fileId=spreadsheet_id, body=permission, sendNotificationEmail=True
            ).execute()

            return ServiceResult(
                success=True,
                message=f"Shared spreadsheet with {email} as {role}",
                data={"spreadsheet_id": spreadsheet_id, "email": email, "role": role},
            )

        except HttpError as error:
            return ServiceResult(
                success=False,
                message=f"Error sharing spreadsheet: {error}",
                error=str(error),
            )
        except Exception as e:
            return ServiceResult(
                success=False,
                message=f"Failed to share spreadsheet: {str(e)}",
                error=str(e),
            )

    async def list_spreadsheets(self, max_results: int = 50) -> ServiceResult:
        try:
            drive_service = build(
                "drive",
                "v3",
                credentials=Credentials.from_service_account_file(
                    SERVICE_ACCOUNT_FILE, scopes=SCOPES
                ),
            )

            results = (
                drive_service.files()
                .list(
                    q="mimeType='application/vnd.google-apps.spreadsheet'",
                    pageSize=max_results,
                    fields="nextPageToken, files(id, name, modifiedTime)",
                )
                .execute()
            )

            files = results.get("files", [])

            return ServiceResult(
                success=True,
                message=f"Found {len(files)} spreadsheets",
                data={"spreadsheets": files},
            )

        except HttpError as error:
            return ServiceResult(
                success=False,
                message=f"Error listing spreadsheets: {error}",
                error=str(error),
            )
        except Exception as e:
            return ServiceResult(
                success=False,
                message=f"Failed to list spreadsheets: {str(e)}",
                error=str(e),
            )

    async def create_worksheet(
        self, spreadsheet_id: str, title: str, rows: int = 1000, columns: int = 26
    ) -> ServiceResult:
        try:
            service = get_google_sheets_service()

            requests = [
                {
                    "addSheet": {
                        "properties": {
                            "title": title,
                            "gridProperties": {
                                "rowCount": rows,
                                "columnCount": columns,
                            },
                        }
                    }
                }
            ]

            body = {"requests": requests}
            service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id, body=body
            ).execute()

            return ServiceResult(
                success=True,
                message=f"Created worksheet: {title}",
                data={
                    "spreadsheet_id": spreadsheet_id,
                    "worksheet_title": title,
                    "rows": rows,
                    "columns": columns,
                },
            )

        except HttpError as error:
            return ServiceResult(
                success=False,
                message=f"Error creating worksheet: {error}",
                error=str(error),
            )
        except Exception as e:
            return ServiceResult(
                success=False,
                message=f"Failed to create worksheet: {str(e)}",
                error=str(e),
            )

    async def read_range(
        self, spreadsheet_id: str, range_name: str, major_dimension: str = "ROWS"
    ) -> ServiceResult:
        try:
            service = get_google_sheets_service()

            result = (
                service.spreadsheets()
                .values()
                .get(
                    spreadsheetId=spreadsheet_id,
                    range=range_name,
                    majorDimension=major_dimension,
                )
                .execute()
            )

            values = result.get("values", [])

            if not values:
                return ServiceResult(
                    success=True,
                    message=f"No data found in range: {range_name}",
                    data={"values": [], "range": range_name},
                )

            formatted_text = f"Data from {range_name} ({len(values)} rows):\n\n"
            for row in values:
                formatted_text += " | ".join(str(cell) for cell in row) + "\n"

            return ServiceResult(
                success=True,
                message=f"Read {len(values)} rows from range: {range_name}",
                data={
                    "values": values,
                    "range": range_name,
                    "row_count": len(values),
                    "formatted_result": formatted_text,
                },
            )

        except HttpError as error:
            return ServiceResult(
                success=False, message=f"Error reading range: {error}", error=str(error)
            )
        except Exception as e:
            return ServiceResult(
                success=False, message=f"Failed to read range: {str(e)}", error=str(e)
            )

    async def write_range(
        self,
        spreadsheet_id: str,
        range_name: str,
        values: List[Any],
        major_dimension: str = "ROWS",
    ) -> ServiceResult:
        try:
            service = get_google_sheets_service()

            body = {"values": values, "majorDimension": major_dimension}

            result = (
                service.spreadsheets()
                .values()
                .update(
                    spreadsheetId=spreadsheet_id,
                    range=range_name,
                    valueInputOption="RAW",
                    body=body,
                )
                .execute()
            )

            updated_cells = result.get("updatedCells", 0)

            return ServiceResult(
                success=True,
                message=f"Updated {updated_cells} cells in range: {range_name}",
                data={
                    "updated_cells": updated_cells,
                    "updated_range": result.get("updatedRange", range_name),
                },
            )

        except HttpError as error:
            return ServiceResult(
                success=False, message=f"Error writing range: {error}", error=str(error)
            )
        except Exception as e:
            return ServiceResult(
                success=False, message=f"Failed to write range: {str(e)}", error=str(e)
            )

    async def append_data(
        self,
        spreadsheet_id: str,
        range_name: str,
        values: List[Any],
        value_input_option: str = "RAW",
    ) -> ServiceResult:
        try:
            service = get_google_sheets_service()

            body = {"values": values}

            result = (
                service.spreadsheets()
                .values()
                .append(
                    spreadsheetId=spreadsheet_id,
                    range=range_name,
                    valueInputOption=value_input_option,
                    body=body,
                )
                .execute()
            )

            updated_cells = result.get("updates", {}).get("updatedCells", 0)

            return ServiceResult(
                success=True,
                message=f"Appended {updated_cells} cells to: {range_name}",
                data={
                    "updated_cells": updated_cells,
                    "updated_range": result.get("updates", {}).get(
                        "updatedRange", range_name
                    ),
                },
            )

        except HttpError as error:
            return ServiceResult(
                success=False,
                message=f"Error appending data: {error}",
                error=str(error),
            )
        except Exception as e:
            return ServiceResult(
                success=False, message=f"Failed to append data: {str(e)}", error=str(e)
            )

    async def clear_range(self, spreadsheet_id: str, range_name: str) -> ServiceResult:
        try:
            service = get_google_sheets_service()

            service.spreadsheets().values().clear(
                spreadsheetId=spreadsheet_id, range=range_name
            ).execute()

            return ServiceResult(
                success=True,
                message=f"Cleared range: {range_name}",
                data={"cleared_range": range_name},
            )

        except HttpError as error:
            return ServiceResult(
                success=False,
                message=f"Error clearing range: {error}",
                error=str(error),
            )
        except Exception as e:
            return ServiceResult(
                success=False, message=f"Failed to clear range: {str(e)}", error=str(e)
            )
