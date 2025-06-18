import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from typing import Dict, Any
import json

from tools.google_sheets import (
    sheets_create_spreadsheet,
    sheets_open_spreadsheet,
    sheets_share_spreadsheet,
    sheets_list_spreadsheets,
    sheets_create_worksheet,
    sheets_read_range,
    sheets_write_range,
    sheets_append_data,
    sheets_clear_range,
)
from tools.tool_schema import ToolActionResult


class TestGoogleSheetsBasic:
    
    @pytest.fixture
    def mock_context(self):
        return Mock()
    
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
    @patch('tools.google_sheets.get_google_sheets_service')
    async def test_create_spreadsheet_basic(self, mock_get_service, mock_context):
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        
        mock_response = {
            'spreadsheetId': '1ABC123',
            'properties': {'title': 'Test Sheet'}
        }
        mock_service.spreadsheets().create().execute.return_value = mock_response
        
        params = {'title': 'Test Sheet'}
        result = await sheets_create_spreadsheet.handle(mock_context, params)
        
        assert result.action is not None
        action_result = await result.action()
        assert isinstance(action_result, ToolActionResult)
        assert '1ABC123' in action_result.content[0]['text']
        assert 'Test Sheet' in action_result.content[0]['text']

    @pytest.mark.asyncio
    @patch('tools.google_sheets.get_google_sheets_service')
    async def test_create_spreadsheet_with_sheets(self, mock_get_service, mock_context):
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        
        mock_response = {
            'spreadsheetId': '1ABC123',
            'properties': {'title': 'Test Sheet'}
        }
        mock_service.spreadsheets().create().execute.return_value = mock_response
        
        params = {
            'title': 'Test Sheet',
            'sheet_names': ['Data', 'Analysis']
        }
        result = await sheets_create_spreadsheet.handle(mock_context, params)
        
        action_result = await result.action()
        assert '1ABC123' in action_result.content[0]['text']
        
        call_args = mock_service.spreadsheets().create.call_args[1]['body']
        assert 'sheets' in call_args
        assert len(call_args['sheets']) == 2
        assert call_args['sheets'][0]['properties']['title'] == 'Data'

    @pytest.mark.asyncio
    @patch('tools.google_sheets.get_google_sheets_service')
    async def test_open_spreadsheet_by_id(self, mock_get_service, mock_context):
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        
        mock_response = {
            'properties': {'title': 'Test Sheet'},
            'sheets': [
                {'properties': {'title': 'Sheet1'}},
                {'properties': {'title': 'Sheet2'}}
            ]
        }
        mock_service.spreadsheets().get().execute.return_value = mock_response
        
        params = {'spreadsheet_id': '1ABC123'}
        result = await sheets_open_spreadsheet.handle(mock_context, params)
        
        action_result = await result.action()
        assert 'Test Sheet' in action_result.content[0]['text']
        assert 'Sheet1, Sheet2' in action_result.content[0]['text']

    @pytest.mark.asyncio
    @patch('tools.google_sheets.get_google_sheets_service')
    async def test_open_spreadsheet_by_url(self, mock_get_service, mock_context):
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        
        mock_response = {
            'properties': {'title': 'Test Sheet'},
            'sheets': [{'properties': {'title': 'Sheet1'}}]
        }
        mock_service.spreadsheets().get().execute.return_value = mock_response
        
        params = {'url': 'https://docs.google.com/spreadsheets/d/1ABC123/edit'}
        result = await sheets_open_spreadsheet.handle(mock_context, params)
        
        action_result = await result.action()
        mock_service.spreadsheets().get.assert_called_with(spreadsheetId='1ABC123')
        assert 'Test Sheet' in action_result.content[0]['text']

    @pytest.mark.asyncio
    @patch('tools.google_sheets.get_google_drive_service')
    async def test_share_spreadsheet(self, mock_get_service, mock_context):
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        
        mock_service.permissions().create().execute.return_value = {}
        
        params = {
            'spreadsheet_id': '1ABC123',
            'email': 'test@example.com',
            'role': 'writer'
        }
        result = await sheets_share_spreadsheet.handle(mock_context, params)
        
        action_result = await result.action()
        assert 'test@example.com' in action_result.content[0]['text']
        assert 'writer' in action_result.content[0]['text']
        
        call_args = mock_service.permissions().create.call_args
        assert call_args[1]['fileId'] == '1ABC123'
        assert call_args[1]['body']['emailAddress'] == 'test@example.com'
        assert call_args[1]['body']['role'] == 'writer'

    @pytest.mark.asyncio
    @patch('tools.google_sheets.get_google_drive_service')
    async def test_list_spreadsheets(self, mock_get_service, mock_context):
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        
        mock_response = {
            'files': [
                {
                    'id': '1ABC123',
                    'name': 'Sheet 1',
                    'createdTime': '2024-01-01T00:00:00Z',
                    'modifiedTime': '2024-01-01T12:00:00Z'
                },
                {
                    'id': '2DEF456',
                    'name': 'Sheet 2',
                    'createdTime': '2024-01-02T00:00:00Z',
                    'modifiedTime': '2024-01-02T12:00:00Z'
                }
            ]
        }
        mock_service.files().list().execute.return_value = mock_response
        
        params = {'max_results': 50}
        result = await sheets_list_spreadsheets.handle(mock_context, params)
        
        action_result = await result.action()
        text = action_result.content[0]['text']
        assert 'Sheet 1' in text
        assert 'Sheet 2' in text
        assert '1ABC123' in text
        assert '2DEF456' in text

    @pytest.mark.asyncio
    @patch('tools.google_sheets.get_google_drive_service')
    async def test_list_spreadsheets_empty(self, mock_get_service, mock_context):
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        
        mock_response = {'files': []}
        mock_service.files().list().execute.return_value = mock_response
        
        params = {}
        result = await sheets_list_spreadsheets.handle(mock_context, params)
        
        action_result = await result.action()
        assert 'No spreadsheets found' in action_result.content[0]['text']

    @pytest.mark.asyncio
    @patch('tools.google_sheets.get_google_sheets_service')
    async def test_create_worksheet(self, mock_get_service, mock_context):
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        
        mock_response = {
            'replies': [
                {'addSheet': {'properties': {'sheetId': 123, 'title': 'New Sheet'}}}
            ]
        }
        mock_service.spreadsheets().batchUpdate().execute.return_value = mock_response
        
        params = {
            'spreadsheet_id': '1ABC123',
            'title': 'New Sheet',
            'rows': 500,
            'columns': 20
        }
        result = await sheets_create_worksheet.handle(mock_context, params)
        
        action_result = await result.action()
        assert 'Created worksheet: New Sheet' in action_result.content[0]['text']
        assert '123' in action_result.content[0]['text']

    @pytest.mark.asyncio
    @patch('tools.google_sheets.get_google_sheets_service')
    async def test_read_range(self, mock_get_service, mock_context):
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        
        mock_response = {
            'values': [
                ['Name', 'Age', 'City'],
                ['John', '25', 'NYC'],
                ['Jane', '30', 'LA']
            ]
        }
        mock_service.spreadsheets().values().get().execute.return_value = mock_response
        
        params = {
            'spreadsheet_id': '1ABC123',
            'range_name': 'Sheet1!A1:C3'
        }
        result = await sheets_read_range.handle(mock_context, params)
        
        action_result = await result.action()
        text = action_result.content[0]['text']
        assert 'John' in text
        assert 'Jane' in text
        assert 'NYC' in text

    @pytest.mark.asyncio
    @patch('tools.google_sheets.get_google_sheets_service')
    async def test_read_range_empty(self, mock_get_service, mock_context):
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        
        mock_response = {}
        mock_service.spreadsheets().values().get().execute.return_value = mock_response
        
        params = {
            'spreadsheet_id': '1ABC123',
            'range_name': 'Sheet1!A1:C3'
        }
        result = await sheets_read_range.handle(mock_context, params)
        
        action_result = await result.action()
        assert 'No data found' in action_result.content[0]['text']

    @pytest.mark.asyncio
    @patch('tools.google_sheets.get_google_sheets_service')
    async def test_write_range(self, mock_get_service, mock_context):
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        
        mock_response = {'updatedCells': 6}
        mock_service.spreadsheets().values().update().execute.return_value = mock_response
        
        params = {
            'spreadsheet_id': '1ABC123',
            'range_name': 'Sheet1!A1:C2',
            'values': [['A1', 'B1', 'C1'], ['A2', 'B2', 'C2']]
        }
        result = await sheets_write_range.handle(mock_context, params)
        
        action_result = await result.action()
        assert 'Updated 6 cells' in action_result.content[0]['text']

    @pytest.mark.asyncio
    @patch('tools.google_sheets.get_google_sheets_service')
    async def test_append_data(self, mock_get_service, mock_context):
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        
        mock_response = {'updates': {'updatedCells': 3}}
        mock_service.spreadsheets().values().append().execute.return_value = mock_response
        
        params = {
            'spreadsheet_id': '1ABC123',
            'range_name': 'Sheet1!A:C',
            'values': [['New', 'Row', 'Data']]
        }
        result = await sheets_append_data.handle(mock_context, params)
        
        action_result = await result.action()
        assert 'Appended 3 cells' in action_result.content[0]['text']

    @pytest.mark.asyncio
    @patch('tools.google_sheets.get_google_sheets_service')
    async def test_clear_range(self, mock_get_service, mock_context):
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        
        mock_response = {'clearedRange': 'Sheet1!A1:C3'}
        mock_service.spreadsheets().values().clear().execute.return_value = mock_response
        
        params = {
            'spreadsheet_id': '1ABC123',
            'range_name': 'Sheet1!A1:C3'
        }
        result = await sheets_clear_range.handle(mock_context, params)
        
        action_result = await result.action()
        assert 'Cleared range: Sheet1!A1:C3' in action_result.content[0]['text']

    @pytest.mark.asyncio
    @patch('tools.google_sheets.get_google_sheets_service')
    async def test_create_spreadsheet_error(self, mock_get_service, mock_context):
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        
        from googleapiclient.errors import HttpError
        import json
        mock_error = HttpError(
            resp=Mock(status=400),
            content=json.dumps({'error': {'message': 'Bad Request'}}).encode()
        )
        mock_service.spreadsheets().create().execute.side_effect = mock_error
        
        params = {'title': 'Test Sheet'}
        result = await sheets_create_spreadsheet.handle(mock_context, params)
        
        action_result = await result.action()
        assert 'Error creating spreadsheet' in action_result.content[0]['text']
        assert 'Bad Request' in action_result.content[0]['text']

    @pytest.mark.asyncio
    @patch('tools.google_sheets.get_google_drive_service')
    async def test_share_spreadsheet_error(self, mock_get_service, mock_context):
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        
        from googleapiclient.errors import HttpError
        import json
        mock_error = HttpError(
            resp=Mock(status=403),
            content=json.dumps({'error': {'message': 'Forbidden'}}).encode()
        )
        mock_service.permissions().create().execute.side_effect = mock_error
        
        params = {
            'spreadsheet_id': '1ABC123',
            'email': 'test@example.com',
            'role': 'writer'
        }
        result = await sheets_share_spreadsheet.handle(mock_context, params)
        
        action_result = await result.action()
        assert 'Error sharing spreadsheet' in action_result.content[0]['text']

    @pytest.mark.asyncio
    async def test_open_spreadsheet_no_params(self, mock_context):
        params = {}
        result = await sheets_open_spreadsheet.handle(mock_context, params)
        
        action_result = await result.action()
        assert 'Either spreadsheet_id or url must be provided' in action_result.content[0]['text'] 