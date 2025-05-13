"""
Google Sheets API client for MCP tools.
"""

import os
import logging
import json
from typing import Dict, Any, Optional, Union, List

# Flag to check if Google API imports are available
GOOGLE_IMPORTS_AVAILABLE = True
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    GOOGLE_IMPORTS_AVAILABLE = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the scopes for Google Sheets API
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


class GoogleSheetsClient:
    """Client for Google Sheets API."""

    def __init__(self, credentials_file: str, token_file: Optional[str] = None):
        """
        Initialize the Google Sheets client.

        Args:
            credentials_file: Path to the credentials.json file
            token_file: Path to the token.json file (if not provided, will be created in same directory as credentials)
        """
        if not GOOGLE_IMPORTS_AVAILABLE:
            raise ImportError(
                "Google API libraries not available. Please install required packages: "
                "pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib"
            )

        self.credentials_file = os.path.abspath(credentials_file)
        if not os.path.exists(self.credentials_file):
            raise FileNotFoundError(
                f"Credentials file not found at {self.credentials_file}"
            )

        if token_file:
            self.token_file = os.path.abspath(token_file)
        else:
            # Create token file in the same directory as credentials file
            token_dir = os.path.dirname(self.credentials_file)
            self.token_file = os.path.join(token_dir, "token.json")

        self.service = None
        self.drive_service = None
        self.creds = None

    def authenticate(self) -> bool:
        """
        Authenticate with Google Sheets API.

        Returns:
            True if authentication was successful, False otherwise
        """
        try:
            # Check if token file exists and is valid
            if os.path.exists(self.token_file):
                self.creds = Credentials.from_authorized_user_info(
                    json.loads(open(self.token_file, "r").read()), SCOPES
                )

            # If there are no valid credentials, authenticate
            if not self.creds or not self.creds.valid:
                if self.creds and self.creds.expired and self.creds.refresh_token:
                    self.creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, SCOPES
                    )
                    self.creds = flow.run_local_server(port=0)

                # Save the credentials
                with open(self.token_file, "w") as token:
                    token.write(self.creds.to_json())

            # Build the services
            self.service = build("sheets", "v4", credentials=self.creds)
            self.drive_service = build("drive", "v3", credentials=self.creds)

            logger.info("Successfully authenticated with Google Sheets API")
            return True

        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return False

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
