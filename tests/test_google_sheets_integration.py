import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from typing import Dict, Any
import json

from tools.google_sheets import get_google_sheets_tools
from core.tool_schema import ToolActionResult


class TestGoogleSheetsIntegration:
    @pytest.fixture
    def mock_context(self):
        return Mock()

    @pytest.fixture
    def google_sheets_tools(self):
        return get_google_sheets_tools(capture_snapshot=False)

    @pytest.fixture
    def mock_sheets_service(self):
        service = Mock()
        service.spreadsheets.return_value = Mock()
        return service

    @pytest.fixture
    def mock_drive_service(self):
        service = Mock()
        service.files.return_value = Mock()
        service.permissions.return_value = Mock()
        return service

    @pytest.mark.asyncio
    @patch("tools.google_sheets.get_google_sheets_service")
    @patch("tools.google_sheets.get_google_drive_service")
    async def test_complete_workflow_create_share_write(
        self, mock_get_drive, mock_get_sheets, mock_context, google_sheets_tools
    ):
        mock_sheets_service = Mock()
        mock_drive_service = Mock()
        mock_get_sheets.return_value = mock_sheets_service
        mock_get_drive.return_value = mock_drive_service

        mock_create_response = {
            "spreadsheetId": "1ABC123",
            "properties": {"title": "Test Workflow"},
        }
        mock_sheets_service.spreadsheets().create().execute.return_value = (
            mock_create_response
        )
        mock_drive_service.permissions().create().execute.return_value = {}
        mock_sheets_service.spreadsheets().values().update().execute.return_value = {
            "updatedCells": 6
        }

        # Get tools
        sheets_create_spreadsheet = next(
            tool
            for tool in google_sheets_tools
            if tool.schema.name == "sheets_create_spreadsheet"
        )
        sheets_share_spreadsheet = next(
            tool
            for tool in google_sheets_tools
            if tool.schema.name == "sheets_share_spreadsheet"
        )
        sheets_write_range = next(
            tool
            for tool in google_sheets_tools
            if tool.schema.name == "sheets_write_range"
        )

        create_params = {"title": "Test Workflow"}
        create_result = await sheets_create_spreadsheet.handle(
            mock_context, create_params
        )
        create_action = await create_result.action()
        assert "1ABC123" in create_action.content[0]["text"]

        share_params = {
            "spreadsheet_id": "1ABC123",
            "email": "user@example.com",
            "role": "writer",
        }
        share_result = await sheets_share_spreadsheet.handle(mock_context, share_params)
        share_action = await share_result.action()
        assert "user@example.com" in share_action.content[0]["text"]

        write_params = {
            "spreadsheet_id": "1ABC123",
            "range_name": "Sheet1!A1:C2",
            "values": [["Name", "Age", "City"], ["John", "25", "NYC"]],
        }
        write_result = await sheets_write_range.handle(mock_context, write_params)
        write_action = await write_result.action()
        assert "6 cells" in write_action.content[0]["text"]

    @pytest.mark.asyncio
    async def test_error_handling_chain(self, mock_context, google_sheets_tools):
        from googleapiclient.errors import HttpError

        with patch("tools.google_sheets.get_google_sheets_service") as mock_get_service:
            mock_service = Mock()
            mock_get_service.return_value = mock_service

            mock_service.spreadsheets().create().execute.side_effect = HttpError(
                resp=Mock(status=403), content=b"Permission denied"
            )

            sheets_create_spreadsheet = next(
                tool
                for tool in google_sheets_tools
                if tool.schema.name == "sheets_create_spreadsheet"
            )

            params = {"title": "Test Sheet"}
            result = await sheets_create_spreadsheet.handle(mock_context, params)
            action_result = await result.action()
            assert "Error creating spreadsheet" in action_result.content[0]["text"]

    @pytest.mark.asyncio
    @patch("tools.google_sheets.get_google_sheets_service")
    async def test_large_data_handling(
        self, mock_get_service, mock_context, google_sheets_tools
    ):
        mock_service = Mock()
        mock_get_service.return_value = mock_service

        large_data = []
        for i in range(1000):
            large_data.append([f"Row{i}", f"Col1-{i}", f"Col2-{i}", f"Col3-{i}"])

        mock_service.spreadsheets().values().update().execute.return_value = {
            "updatedCells": 4000
        }

        sheets_write_range = next(
            tool
            for tool in google_sheets_tools
            if tool.schema.name == "sheets_write_range"
        )

        params = {
            "spreadsheet_id": "1ABC123",
            "range_name": "Sheet1!A1:D1000",
            "values": large_data,
        }
        result = await sheets_write_range.handle(mock_context, params)
        action_result = await result.action()
        assert "4000 cells" in action_result.content[0]["text"]

    @pytest.mark.asyncio
    @patch("tools.google_sheets.get_google_sheets_service")
    async def test_unicode_data_handling(
        self, mock_get_service, mock_context, google_sheets_tools
    ):
        mock_service = Mock()
        mock_get_service.return_value = mock_service

        unicode_data = [
            ["Tên", "Tuổi", "Thành phố"],
            ["Nguyễn Văn A", "25", "Hà Nội"],
            ["Trần Thị B", "30", "Hồ Chí Minh"],
        ]

        mock_service.spreadsheets().values().update().execute.return_value = {
            "updatedCells": 9
        }

        sheets_write_range = next(
            tool
            for tool in google_sheets_tools
            if tool.schema.name == "sheets_write_range"
        )

        params = {
            "spreadsheet_id": "1ABC123",
            "range_name": "Sheet1!A1:C3",
            "values": unicode_data,
        }
        result = await sheets_write_range.handle(mock_context, params)
        action_result = await result.action()
        assert "9 cells" in action_result.content[0]["text"]

    @pytest.mark.asyncio
    async def test_edge_case_empty_values(self, mock_context, google_sheets_tools):
        with patch("tools.google_sheets.get_google_sheets_service") as mock_get_service:
            mock_service = Mock()
            mock_get_service.return_value = mock_service

            mock_service.spreadsheets().values().get().execute.return_value = {
                "values": []
            }

            sheets_read_range = next(
                tool
                for tool in google_sheets_tools
                if tool.schema.name == "sheets_read_range"
            )

            params = {"spreadsheet_id": "1ABC123", "range_name": "Sheet1!A1:A10"}
            result = await sheets_read_range.handle(mock_context, params)
            action_result = await result.action()
            assert "No data found" in action_result.content[0]["text"]

    @pytest.mark.asyncio
    async def test_url_id_extraction_edge_cases(
        self, mock_context, google_sheets_tools
    ):
        with patch("tools.google_sheets.get_google_sheets_service") as mock_get_service:
            mock_service = Mock()
            mock_get_service.return_value = mock_service

            mock_service.spreadsheets().values().get().execute.return_value = {
                "values": [["test"]]
            }

            sheets_read_range = next(
                tool
                for tool in google_sheets_tools
                if tool.schema.name == "sheets_read_range"
            )

            # Test with Google Sheets URL
            params = {
                "spreadsheet_id": "https://docs.google.com/spreadsheets/d/1ABC123/edit#gid=0",
                "range_name": "Sheet1!A1",
            }
            result = await sheets_read_range.handle(mock_context, params)
            action_result = await result.action()
            assert "test" in action_result.content[0]["text"]
