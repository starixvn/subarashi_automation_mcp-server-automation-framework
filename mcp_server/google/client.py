import os
import logging
import json
from typing import Dict, Any, Optional, List

GOOGLE_IMPORTS_AVAILABLE = True
try:
    from google.oauth2.service_account import Credentials
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    GOOGLE_IMPORTS_AVAILABLE = False

from mcp_server.config.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GoogleSheetsClient:
    """Client for Google Sheets API using Service Account Authentication."""

    def __init__(self, credentials_file: str):
        """
        Initialize the Google Sheets client with service account credentials.

        Args:
            credentials_file: Path to the service account credentials JSON file
        """
        if not GOOGLE_IMPORTS_AVAILABLE:
            raise ImportError(
                "Google API libraries not available. Please install required packages: "
                "pip install google-api-python-client google-auth"
            )

        self.credentials_file = os.path.abspath(credentials_file)
        if not os.path.exists(self.credentials_file):
            raise FileNotFoundError(
                f"Service account credentials file not found at {self.credentials_file}"
            )

        self.service = None
        self.drive_service = None
        self.creds = None
        self.scopes = settings.GOOGLE_SCOPES

    def authenticate(self) -> bool:
        """
        Authenticate with Google Sheets API using service account credentials.

        Returns:
            True if authentication was successful, False otherwise
        """
        try:
            self.creds = Credentials.from_service_account_file(
                self.credentials_file, scopes=self.scopes
            )

            self.service = build("sheets", "v4", credentials=self.creds)
            self.drive_service = build("drive", "v3", credentials=self.creds)

            logger.info("Successfully authenticated with Google Sheets API using service account")
            return True

        except Exception as e:
            logger.error(f"Service account authentication error: {str(e)}")
            return False

    def get_service_account_email(self) -> Optional[str]:
        """
        Get the email address of the service account.

        Returns:
            Service account email if available, None otherwise
        """
        try:
            with open(self.credentials_file, 'r') as f:
                creds_data = json.load(f)
                return creds_data.get('client_email')
        except Exception as e:
            logger.error(f"Error reading service account email: {str(e)}")
            return None

    def read_sheet(
        self, spreadsheet_id: str, range_name: str, include_headers: bool = True
    ) -> List[List[Any]]:
        """
        Read data from a Google Sheet.

        Args:
            spreadsheet_id: ID of the Google Sheet
            range_name: Range to read (e.g., 'Sheet1!A1:D10')
            include_headers: Whether to include headers in the result

        Returns:
            2D list of values from the sheet
        """
        if not self.service:
            raise ValueError("Not authenticated. Call authenticate() first.")

        sheet = self.service.spreadsheets()
        result = (
            sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
        )

        return result.get("values", [])

    def write_sheet(
        self, spreadsheet_id: str, range_name: str, values: List[List[Any]]
    ) -> Dict[str, Any]:
        """
        Write data to a Google Sheet, replacing existing data.

        Args:
            spreadsheet_id: ID of the Google Sheet
            range_name: Range to write to (e.g., 'Sheet1!A1')
            values: 2D list of values to write

        Returns:
            Response from the API
        """
        if not self.service:
            raise ValueError("Not authenticated. Call authenticate() first.")

        body = {"values": values}

        try:
            result = (
                self.service.spreadsheets()
                .values()
                .update(
                    spreadsheetId=spreadsheet_id,
                    range=range_name,
                    valueInputOption="USER_ENTERED",
                    body=body,
                )
                .execute()
            )
            return result
        except Exception as e:
            return {"error": str(e)}

    def append_sheet(
        self, spreadsheet_id: str, range_name: str, values: List[List[Any]]
    ) -> Dict[str, Any]:
        """
        Append data to a Google Sheet.

        Args:
            spreadsheet_id: ID of the Google Sheet
            range_name: Range to append to (e.g., 'Sheet1!A1')
            values: 2D list of values to append

        Returns:
            Response from the API
        """
        if not self.service:
            raise ValueError("Not authenticated. Call authenticate() first.")

        body = {"values": values}

        try:
            result = (
                self.service.spreadsheets()
                .values()
                .append(
                    spreadsheetId=spreadsheet_id,
                    range=range_name,
                    valueInputOption="USER_ENTERED",
                    insertDataOption="INSERT_ROWS",
                    body=body,
                )
                .execute()
            )
            return result
        except Exception as e:
            return {"error": str(e)}

    def clear_sheet(self, spreadsheet_id: str, range_name: str) -> Dict[str, Any]:
        """
        Clear a range in a Google Sheet.

        Args:
            spreadsheet_id: ID of the Google Sheet
            range_name: Range to clear (e.g., 'Sheet1!A1:D10')

        Returns:
            Response from the API
        """
        if not self.service:
            raise ValueError("Not authenticated. Call authenticate() first.")

        try:
            result = (
                self.service.spreadsheets()
                .values()
                .clear(spreadsheetId=spreadsheet_id, range=range_name, body={})
                .execute()
            )
            return result
        except Exception as e:
            return {"error": str(e)}

    def create_sheet(self, spreadsheet_id: str, title: str) -> Dict[str, Any]:
        """
        Create a new sheet (tab) in an existing spreadsheet.

        Args:
            spreadsheet_id: ID of the Google Sheet
            title: Title for the new sheet

        Returns:
            Response from the API
        """
        if not self.service:
            raise ValueError("Not authenticated. Call authenticate() first.")

        body = {"requests": [{"addSheet": {"properties": {"title": title}}}]}

        try:
            result = (
                self.service.spreadsheets()
                .batchUpdate(spreadsheetId=spreadsheet_id, body=body)
                .execute()
            )
            return result
        except Exception as e:
            return {"error": str(e)}

    def get_sheets(self, spreadsheet_id: str) -> Dict[str, Any]:
        """
        Get information about sheets in a spreadsheet.

        Args:
            spreadsheet_id: ID of the Google Sheet

        Returns:
            Spreadsheet metadata including sheets
        """
        if not self.service:
            raise ValueError("Not authenticated. Call authenticate() first.")

        try:
            result = (
                self.service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
            )
            return result
        except Exception as e:
            return {"error": str(e)}
