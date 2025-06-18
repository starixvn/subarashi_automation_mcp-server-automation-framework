import pytest
from unittest.mock import Mock, patch
from typing import Dict, Any

from tools.google_sheets_advanced import (
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
    parse_range_to_grid_range,
)
from tools.tool_schema import ToolActionResult


class TestGoogleSheetsAdvanced:
    
    @pytest.fixture
    def mock_context(self):
        return Mock()

    def test_parse_range_to_grid_range(self):
        result = parse_range_to_grid_range('A1:C3', 0)
        expected = {
            'sheetId': 0,
            'startRowIndex': 0,
            'endRowIndex': 3,
            'startColumnIndex': 0,
            'endColumnIndex': 3
        }
        assert result == expected

    def test_parse_range_to_grid_range_with_sheet(self):
        result = parse_range_to_grid_range('Sheet1!B2:D4', 1)
        expected = {
            'sheetId': 1,
            'startRowIndex': 1,
            'endRowIndex': 4,
            'startColumnIndex': 1,
            'endColumnIndex': 4
        }
        assert result == expected

    def test_parse_range_single_cell(self):
        result = parse_range_to_grid_range('A1', 0)
        expected = {
            'sheetId': 0,
            'startRowIndex': 0,
            'endRowIndex': 1,
            'startColumnIndex': 0,
            'endColumnIndex': 1
        }
        assert result == expected

    @pytest.mark.asyncio
    @patch('tools.google_sheets_advanced.get_google_sheets_service')
    async def test_format_cells_bold(self, mock_get_service, mock_context):
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        
        mock_service.spreadsheets().batchUpdate().execute.return_value = {}
        
        params = {
            'spreadsheet_id': '1ABC123',
            'range_name': 'A1:C3',
            'bold': True,
            'font_size': 12
        }
        result = await sheets_format_cells.handle(mock_context, params)
        
        action_result = await result.action()
        assert 'Formatted cells in range: A1:C3' in action_result.content[0]['text']
        
        call_args = mock_service.spreadsheets().batchUpdate.call_args[1]['body']
        requests = call_args['requests']
        assert len(requests) == 1
        assert 'repeatCell' in requests[0]

    @pytest.mark.asyncio
    @patch('tools.google_sheets_advanced.get_google_sheets_service')
    async def test_format_cells_colors(self, mock_get_service, mock_context):
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        
        mock_service.spreadsheets().batchUpdate().execute.return_value = {}
        
        params = {
            'spreadsheet_id': '1ABC123',
            'range_name': 'A1:C3',
            'background_color': {'red': 1.0, 'green': 0.5, 'blue': 0.0},
            'text_color': {'red': 0.0, 'green': 0.0, 'blue': 1.0}
        }
        result = await sheets_format_cells.handle(mock_context, params)
        
        action_result = await result.action()
        assert 'Formatted cells' in action_result.content[0]['text']

    @pytest.mark.asyncio
    @patch('tools.google_sheets_advanced.get_google_sheets_service')
    async def test_merge_cells(self, mock_get_service, mock_context):
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        
        mock_service.spreadsheets().batchUpdate().execute.return_value = {}
        
        params = {
            'spreadsheet_id': '1ABC123',
            'range_name': 'A1:C3',
            'merge_type': 'MERGE_ALL'
        }
        result = await sheets_merge_cells.handle(mock_context, params)
        
        action_result = await result.action()
        assert 'Merged cells in range: A1:C3' in action_result.content[0]['text']
        
        call_args = mock_service.spreadsheets().batchUpdate.call_args[1]['body']
        requests = call_args['requests']
        assert requests[0]['mergeCells']['mergeType'] == 'MERGE_ALL'

    @pytest.mark.asyncio
    @patch('tools.google_sheets_advanced.get_google_sheets_service')
    async def test_sort_range_ascending(self, mock_get_service, mock_context):
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        
        mock_service.spreadsheets().batchUpdate().execute.return_value = {}
        
        params = {
            'spreadsheet_id': '1ABC123',
            'range_name': 'A1:C10',
            'sort_column': 0,
            'ascending': True
        }
        result = await sheets_sort_range.handle(mock_context, params)
        
        action_result = await result.action()
        assert 'ascending order' in action_result.content[0]['text']
        
        call_args = mock_service.spreadsheets().batchUpdate.call_args[1]['body']
        sort_spec = call_args['requests'][0]['sortRange']['sortSpecs'][0]
        assert sort_spec['dimensionIndex'] == 0
        assert sort_spec['sortOrder'] == 'ASCENDING'

    @pytest.mark.asyncio
    @patch('tools.google_sheets_advanced.get_google_sheets_service')
    async def test_sort_range_descending(self, mock_get_service, mock_context):
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        
        mock_service.spreadsheets().batchUpdate().execute.return_value = {}
        
        params = {
            'spreadsheet_id': '1ABC123',
            'range_name': 'A1:C10',
            'sort_column': 1,
            'ascending': False
        }
        result = await sheets_sort_range.handle(mock_context, params)
        
        action_result = await result.action()
        assert 'descending order' in action_result.content[0]['text']

    @pytest.mark.asyncio
    @patch('tools.google_sheets_advanced.get_google_sheets_service')
    async def test_insert_rows(self, mock_get_service, mock_context):
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        
        mock_service.spreadsheets().batchUpdate().execute.return_value = {}
        
        params = {
            'spreadsheet_id': '1ABC123',
            'sheet_id': 0,
            'start_index': 5,
            'end_index': 10
        }
        result = await sheets_insert_rows.handle(mock_context, params)
        
        action_result = await result.action()
        assert 'Inserted 5 rows' in action_result.content[0]['text']
        assert 'starting at index 5' in action_result.content[0]['text']
        
        call_args = mock_service.spreadsheets().batchUpdate.call_args[1]['body']
        insert_request = call_args['requests'][0]['insertDimension']
        assert insert_request['range']['dimension'] == 'ROWS'
        assert insert_request['range']['startIndex'] == 5
        assert insert_request['range']['endIndex'] == 10

    @pytest.mark.asyncio
    @patch('tools.google_sheets_advanced.get_google_sheets_service')
    async def test_insert_columns(self, mock_get_service, mock_context):
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        
        mock_service.spreadsheets().batchUpdate().execute.return_value = {}
        
        params = {
            'spreadsheet_id': '1ABC123',
            'sheet_id': 0,
            'start_index': 2,
            'end_index': 5
        }
        result = await sheets_insert_columns.handle(mock_context, params)
        
        action_result = await result.action()
        assert 'Inserted 3 columns' in action_result.content[0]['text']
        
        call_args = mock_service.spreadsheets().batchUpdate.call_args[1]['body']
        insert_request = call_args['requests'][0]['insertDimension']
        assert insert_request['range']['dimension'] == 'COLUMNS'

    @pytest.mark.asyncio
    @patch('tools.google_sheets_advanced.get_google_sheets_service')
    async def test_delete_rows(self, mock_get_service, mock_context):
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        
        mock_service.spreadsheets().batchUpdate().execute.return_value = {}
        
        params = {
            'spreadsheet_id': '1ABC123',
            'sheet_id': 0,
            'start_index': 3,
            'end_index': 6
        }
        result = await sheets_delete_rows.handle(mock_context, params)
        
        action_result = await result.action()
        assert 'Deleted 3 rows' in action_result.content[0]['text']
        
        call_args = mock_service.spreadsheets().batchUpdate.call_args[1]['body']
        delete_request = call_args['requests'][0]['deleteDimension']
        assert delete_request['range']['dimension'] == 'ROWS'

    @pytest.mark.asyncio
    @patch('tools.google_sheets_advanced.get_google_sheets_service')
    async def test_delete_columns(self, mock_get_service, mock_context):
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        
        mock_service.spreadsheets().batchUpdate().execute.return_value = {}
        
        params = {
            'spreadsheet_id': '1ABC123',
            'sheet_id': 0,
            'start_index': 1,
            'end_index': 3
        }
        result = await sheets_delete_columns.handle(mock_context, params)
        
        action_result = await result.action()
        assert 'Deleted 2 columns' in action_result.content[0]['text']

    @pytest.mark.asyncio
    @patch('tools.google_sheets_advanced.get_google_sheets_service')
    async def test_find_replace(self, mock_get_service, mock_context):
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        
        mock_response = {
            'replies': [
                {'findReplace': {'occurrencesChanged': 5}}
            ]
        }
        mock_service.spreadsheets().batchUpdate().execute.return_value = mock_response
        
        params = {
            'spreadsheet_id': '1ABC123',
            'find_text': 'old_text',
            'replace_text': 'new_text',
            'match_case': True,
            'match_entire_cell': False
        }
        result = await sheets_find_replace.handle(mock_context, params)
        
        action_result = await result.action()
        assert 'Replaced 5 occurrences' in action_result.content[0]['text']
        assert 'old_text' in action_result.content[0]['text']
        assert 'new_text' in action_result.content[0]['text']

    @pytest.mark.asyncio
    @patch('tools.google_sheets_advanced.get_google_sheets_service')
    async def test_find_replace_with_sheet_id(self, mock_get_service, mock_context):
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        
        mock_response = {
            'replies': [
                {'findReplace': {'occurrencesChanged': 2}}
            ]
        }
        mock_service.spreadsheets().batchUpdate().execute.return_value = mock_response
        
        params = {
            'spreadsheet_id': '1ABC123',
            'find_text': 'search',
            'replace_text': 'replace',
            'sheet_id': 123
        }
        result = await sheets_find_replace.handle(mock_context, params)
        
        action_result = await result.action()
        assert 'Replaced 2 occurrences' in action_result.content[0]['text']

    @pytest.mark.asyncio
    @patch('tools.google_sheets_advanced.get_google_sheets_service')
    async def test_add_formula(self, mock_get_service, mock_context):
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        
        mock_service.spreadsheets().values().update().execute.return_value = {}
        
        params = {
            'spreadsheet_id': '1ABC123',
            'range_name': 'A1',
            'formula': 'SUM(B1:B10)'
        }
        result = await sheets_add_formula.handle(mock_context, params)
        
        action_result = await result.action()
        assert 'Added formula' in action_result.content[0]['text']
        assert '=SUM(B1:B10)' in action_result.content[0]['text']
        
        call_args = mock_service.spreadsheets().values().update.call_args
        assert call_args[1]['valueInputOption'] == 'USER_ENTERED'
        assert call_args[1]['body']['values'] == [['=SUM(B1:B10)']]

    @pytest.mark.asyncio
    @patch('tools.google_sheets_advanced.get_google_sheets_service')
    async def test_freeze_rows(self, mock_get_service, mock_context):
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        
        mock_service.spreadsheets().batchUpdate().execute.return_value = {}
        
        params = {
            'spreadsheet_id': '1ABC123',
            'sheet_id': 0,
            'frozen_row_count': 3
        }
        result = await sheets_freeze_rows.handle(mock_context, params)
        
        action_result = await result.action()
        assert 'Froze 3 rows' in action_result.content[0]['text']
        
        call_args = mock_service.spreadsheets().batchUpdate.call_args[1]['body']
        update_request = call_args['requests'][0]['updateSheetProperties']
        assert update_request['properties']['gridProperties']['frozenRowCount'] == 3

    @pytest.mark.asyncio
    @patch('tools.google_sheets_advanced.get_google_sheets_service')
    async def test_freeze_columns(self, mock_get_service, mock_context):
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        
        mock_service.spreadsheets().batchUpdate().execute.return_value = {}
        
        params = {
            'spreadsheet_id': '1ABC123',
            'sheet_id': 0,
            'frozen_column_count': 2
        }
        result = await sheets_freeze_columns.handle(mock_context, params)
        
        action_result = await result.action()
        assert 'Froze 2 columns' in action_result.content[0]['text']

    @pytest.mark.asyncio
    @patch('tools.google_sheets_advanced.get_google_sheets_service')
    async def test_delete_worksheet(self, mock_get_service, mock_context):
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        
        mock_service.spreadsheets().batchUpdate().execute.return_value = {}
        
        params = {
            'spreadsheet_id': '1ABC123',
            'sheet_id': 123
        }
        result = await sheets_delete_worksheet.handle(mock_context, params)
        
        action_result = await result.action()
        assert 'Deleted worksheet with ID: 123' in action_result.content[0]['text']
        
        call_args = mock_service.spreadsheets().batchUpdate.call_args[1]['body']
        delete_request = call_args['requests'][0]['deleteSheet']
        assert delete_request['sheetId'] == 123

    @pytest.mark.asyncio
    @patch('tools.google_sheets_advanced.get_google_sheets_service')
    async def test_rename_worksheet(self, mock_get_service, mock_context):
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        
        mock_service.spreadsheets().batchUpdate().execute.return_value = {}
        
        params = {
            'spreadsheet_id': '1ABC123',
            'sheet_id': 123,
            'new_title': 'Renamed Sheet'
        }
        result = await sheets_rename_worksheet.handle(mock_context, params)
        
        action_result = await result.action()
        assert 'Renamed worksheet to: Renamed Sheet' in action_result.content[0]['text']
        
        call_args = mock_service.spreadsheets().batchUpdate.call_args[1]['body']
        update_request = call_args['requests'][0]['updateSheetProperties']
        assert update_request['properties']['title'] == 'Renamed Sheet'

    @pytest.mark.asyncio
    @patch('tools.google_sheets_advanced.get_google_sheets_service')
    async def test_list_worksheets(self, mock_get_service, mock_context):
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        
        mock_response = {
            'sheets': [
                {
                    'properties': {
                        'title': 'Sheet1',
                        'sheetId': 0,
                        'gridProperties': {'rowCount': 1000, 'columnCount': 26}
                    }
                },
                {
                    'properties': {
                        'title': 'Sheet2',
                        'sheetId': 123,
                        'gridProperties': {'rowCount': 500, 'columnCount': 10}
                    }
                }
            ]
        }
        mock_service.spreadsheets().get().execute.return_value = mock_response
        
        params = {'spreadsheet_id': '1ABC123'}
        result = await sheets_list_worksheets.handle(mock_context, params)
        
        action_result = await result.action()
        text = action_result.content[0]['text']
        assert 'Sheet1' in text
        assert 'Sheet2' in text
        assert 'ID: 0' in text
        assert 'ID: 123' in text
        assert '1000x26' in text
        assert '500x10' in text

    @pytest.mark.asyncio
    @patch('tools.google_sheets_advanced.get_google_sheets_service')
    async def test_list_worksheets_empty(self, mock_get_service, mock_context):
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        
        mock_response = {'sheets': []}
        mock_service.spreadsheets().get().execute.return_value = mock_response
        
        params = {'spreadsheet_id': '1ABC123'}
        result = await sheets_list_worksheets.handle(mock_context, params)
        
        action_result = await result.action()
        assert 'No worksheets found' in action_result.content[0]['text']

    @pytest.mark.asyncio
    @patch('tools.google_sheets_advanced.get_google_sheets_service')
    async def test_update_cell(self, mock_get_service, mock_context):
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        
        mock_service.spreadsheets().values().update().execute.return_value = {}
        
        params = {
            'spreadsheet_id': '1ABC123',
            'range_name': 'A1',
            'value': 'Updated Value'
        }
        result = await sheets_update_cell.handle(mock_context, params)
        
        action_result = await result.action()
        assert 'Updated cell A1 with value: Updated Value' in action_result.content[0]['text']
        
        call_args = mock_service.spreadsheets().values().update.call_args
        assert call_args[1]['body']['values'] == [['Updated Value']]
        assert call_args[1]['valueInputOption'] == 'RAW'

    @pytest.mark.asyncio
    @patch('tools.google_sheets_advanced.get_google_sheets_service')
    async def test_format_cells_error(self, mock_get_service, mock_context):
        from googleapiclient.errors import HttpError
        
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        
        mock_service.spreadsheets().batchUpdate().execute.side_effect = HttpError(
            resp=Mock(status=400),
            content=b'Invalid range'
        )
        
        params = {
            'spreadsheet_id': '1ABC123',
            'range_name': 'InvalidRange',
            'bold': True
        }
        result = await sheets_format_cells.handle(mock_context, params)
        
        action_result = await result.action()
        assert 'Error formatting cells' in action_result.content[0]['text']

    @pytest.mark.asyncio
    @patch('tools.google_sheets_advanced.get_google_sheets_service')
    async def test_sort_range_error(self, mock_get_service, mock_context):
        from googleapiclient.errors import HttpError
        
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        
        mock_service.spreadsheets().batchUpdate().execute.side_effect = HttpError(
            resp=Mock(status=403),
            content=b'Permission denied'
        )
        
        params = {
            'spreadsheet_id': '1ABC123',
            'range_name': 'A1:C10',
            'sort_column': 0
        }
        result = await sheets_sort_range.handle(mock_context, params)
        
        action_result = await result.action()
        assert 'Error sorting range' in action_result.content[0]['text'] 
