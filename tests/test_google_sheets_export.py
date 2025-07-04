import pytest
import os
import tempfile
import json
import csv
from unittest.mock import Mock, patch, mock_open, MagicMock
from io import BytesIO, StringIO

from tools.google_sheets_export import (
    sheets_export_sheet,
    sheets_import_csv,
    sheets_export_range,
    sheets_create_from_csv,
    sheets_backup_spreadsheet,
)
from tools.tool_schema import ToolActionResult


# Disable autouse fixture for this test class
class TestGoogleSheetsExport:
    
    @pytest.fixture
    def mock_context(self):
        return Mock()

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir

    # Override autouse fixture để disable
    @pytest.fixture(autouse=True)
    def mock_all_google_services(self):
        # Do nothing, let tests handle their own mocking
        yield

    @pytest.mark.asyncio
    @patch('tools.google_sheets_export.get_google_drive_service')
    @patch('builtins.open', new_callable=mock_open)
    async def test_export_sheet_csv(self, mock_file, mock_get_service, mock_context, temp_dir):
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        
        mock_request = Mock()
        mock_service.files().export_media.return_value = mock_request
        
        mock_downloader = Mock()
        mock_downloader.next_chunk.side_effect = [(None, False), (None, True)]
        
        csv_data = b'Name,Age,City\nJohn,25,NYC\nJane,30,LA'
        
        with patch('tools.google_sheets_export.MediaIoBaseDownload') as mock_download_class:
            mock_download_instance = Mock()
            mock_download_class.return_value = mock_download_instance
            mock_download_instance.next_chunk.side_effect = [(None, False), (None, True)]
            
            with patch('tools.google_sheets_export.io.BytesIO') as mock_bytesio:
                mock_fh = Mock()
                mock_fh.getvalue.return_value = csv_data
                mock_bytesio.return_value = mock_fh
                
                output_file = os.path.join(temp_dir, 'output.csv')
                params = {
                    'spreadsheet_id': '1ABC123',
                    'format': 'csv',
                    'output_file': output_file
                }
                result = await sheets_export_sheet.handle(mock_context, params)
                
                action_result = await result.action()
                assert 'Exported sheet to' in action_result.content[0]['text']
                assert 'CSV format' in action_result.content[0]['text']

    @pytest.mark.asyncio
    @patch('tools.google_sheets_export.get_google_drive_service')
    async def test_export_sheet_invalid_format(self, mock_get_service, mock_context):
        params = {
            'spreadsheet_id': '1ABC123',
            'format': 'invalid_format',
            'output_file': 'output.txt'
        }
        result = await sheets_export_sheet.handle(mock_context, params)
        
        action_result = await result.action()
        assert 'Unsupported format' in action_result.content[0]['text']

    @pytest.mark.asyncio
    @patch('tools.google_sheets_export.get_google_drive_service')
    async def test_export_sheet_with_sheet_id(self, mock_get_service, mock_context, temp_dir):
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        
        with patch('tools.google_sheets_export.MediaIoBaseDownload') as mock_download_class:
            mock_download_instance = Mock()
            mock_download_class.return_value = mock_download_instance
            mock_download_instance.next_chunk.side_effect = [(None, False), (None, True)]
            
            with patch('tools.google_sheets_export.io.BytesIO') as mock_bytesio:
                mock_fh = Mock()
                mock_fh.getvalue.return_value = b'test data'
                mock_bytesio.return_value = mock_fh
                
                with patch('builtins.open', mock_open()):
                    output_file = os.path.join(temp_dir, 'output.pdf')
                    params = {
                        'spreadsheet_id': '1ABC123',
                        'format': 'pdf',
                        'sheet_id': 123,
                        'output_file': output_file
                    }
                    result = await sheets_export_sheet.handle(mock_context, params)
                    
                    action_result = await result.action()
                    assert 'PDF format' in action_result.content[0]['text']
                    
                    call_args = mock_service.files().export_media.call_args
                    assert 'gid' in call_args[1]
                    assert call_args[1]['gid'] == 123

    @pytest.mark.asyncio
    async def test_import_csv(self, mock_context, temp_dir):
        # Tạo file CSV trước khi gọi handle
        csv_file = os.path.join(temp_dir, 'test.csv')
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Name', 'Age', 'City'])
            writer.writerow(['John', '25', 'NYC'])
        
        # Đảm bảo file tồn tại
        assert os.path.exists(csv_file), f"CSV file not found at {csv_file}"
        
        # Mock service manually, bypassing autouse fixture
        with patch('tools.google_sheets_export.get_google_sheets_service') as mock_get_service:
            mock_service = Mock()
            mock_get_service.return_value = mock_service
            
            mock_response = {'updatedCells': 6}
            mock_service.spreadsheets().values().update().execute.return_value = mock_response
            
            params = {
                'spreadsheet_id': '1ABC123',
                'csv_file': csv_file,
                'sheet_name': 'Data',
                'range_name': 'A1'
            }
            result = await sheets_import_csv.handle(mock_context, params)
            
            # Kiểm tra file vẫn tồn tại trước khi gọi action
            assert os.path.exists(csv_file), f"CSV file disappeared before action at {csv_file}"
            
            action_result = await result.action()
            assert 'Imported CSV data: 6 cells updated' in action_result.content[0]['text']
            
            call_args = mock_service.spreadsheets().values().update.call_args
            assert call_args[1]['range'] == 'Data!A1'
            assert call_args[1]['body']['values'] == [['Name', 'Age', 'City'], ['John', '25', 'NYC']]

    @pytest.mark.asyncio
    async def test_import_csv_with_clear(self, mock_context, temp_dir):
        csv_file = os.path.join(temp_dir, 'test.csv')
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['A', 'B', 'C'])
        
        assert os.path.exists(csv_file), f"CSV file not created at {csv_file}"
        
        with patch('tools.google_sheets_export.get_google_sheets_service') as mock_get_service:
            mock_service = Mock()
            mock_get_service.return_value = mock_service
            
            mock_service.spreadsheets().values().clear().execute.return_value = {}
            mock_service.spreadsheets().values().update().execute.return_value = {'updatedCells': 3}
            
            params = {
                'spreadsheet_id': '1ABC123',
                'csv_file': csv_file,
                'clear_existing': True
            }
            result = await sheets_import_csv.handle(mock_context, params)
            
            action_result = await result.action()
            assert 'Imported CSV data' in action_result.content[0]['text']
            clear_calls = mock_service.spreadsheets().values().clear.call_args_list
            assert len(clear_calls) >= 1
            mock_service.spreadsheets().values().clear().execute.assert_called()

    @pytest.mark.asyncio
    async def test_import_csv_file_not_found(self, mock_context):
        params = {
            'spreadsheet_id': '1ABC123',
            'csv_file': 'nonexistent.csv'
        }
        result = await sheets_import_csv.handle(mock_context, params)
        
        action_result = await result.action()
        assert 'CSV file not found' in action_result.content[0]['text']

    @pytest.mark.asyncio
    @patch('tools.google_sheets_export.get_google_sheets_service')
    async def test_import_csv_empty_file(self, mock_get_service, mock_context, temp_dir):
        csv_file = os.path.join(temp_dir, 'empty.csv')
        with open(csv_file, 'w', encoding='utf-8') as f:
            pass
        
        params = {
            'spreadsheet_id': '1ABC123',
            'csv_file': csv_file
        }
        result = await sheets_import_csv.handle(mock_context, params)
        
        action_result = await result.action()
        assert 'CSV file is empty' in action_result.content[0]['text']

    @pytest.mark.asyncio
    async def test_export_range_csv(self, mock_context, temp_dir):
        with patch('tools.google_sheets_export.get_google_sheets_service') as mock_get_service:
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
            
            output_file = os.path.join(temp_dir, 'range_output.csv')
            params = {
                'spreadsheet_id': '1ABC123',
                'range_name': 'Sheet1!A1:C3',
                'format': 'csv',
                'output_file': output_file
            }
            result = await sheets_export_range.handle(mock_context, params)
            
            action_result = await result.action()
            assert 'Exported range Sheet1!A1:C3 to' in action_result.content[0]['text']
            assert 'CSV format' in action_result.content[0]['text']
            
            # Kiểm tra file được tạo và có nội dung đúng
            assert os.path.exists(output_file)
            with open(output_file, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                rows = list(reader)
                assert len(rows) >= 2  # Ít nhất header và 1 dòng data
                assert rows[0] == ['Name', 'Age', 'City']
                assert rows[1] == ['John', '25', 'NYC']

    @pytest.mark.asyncio
    @patch('tools.google_sheets_export.get_google_sheets_service')
    async def test_export_range_json(self, mock_get_service, mock_context, temp_dir):
        with patch('tools.google_sheets_export.get_google_sheets_service') as mock_get_service:
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
            
            output_file = os.path.join(temp_dir, 'range_output.json')
            params = {
                'spreadsheet_id': '1ABC123',
                'range_name': 'Sheet1!A1:C3',
                'format': 'json',
                'output_file': output_file
            }
            result = await sheets_export_range.handle(mock_context, params)
            
            action_result = await result.action()
            assert 'JSON format' in action_result.content[0]['text']
            
            # Kiểm tra file JSON được tạo và có nội dung đúng
            assert os.path.exists(output_file)
            with open(output_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                assert len(data) == 2  # 2 dòng data (không tính header)
                assert data[0]['Name'] == 'John'
                assert data[1]['Name'] == 'Jane'

    @pytest.mark.asyncio
    @patch('tools.google_sheets_export.get_google_sheets_service')
    async def test_export_range_no_data(self, mock_get_service, mock_context):
        with patch('tools.google_sheets_export.get_google_sheets_service') as mock_get_service:
            mock_service = Mock()
            mock_get_service.return_value = mock_service
            
            # Mock empty response
            mock_response = {}
            mock_service.spreadsheets().values().get().execute.return_value = mock_response
            
            params = {
                'spreadsheet_id': '1ABC123',
                'range_name': 'Sheet1!A1:C3',
                'format': 'csv',
                'output_file': 'output.csv'
            }
            result = await sheets_export_range.handle(mock_context, params)
            
            action_result = await result.action()
            assert 'No data found in range' in action_result.content[0]['text']

    @pytest.mark.asyncio
    @patch('tools.google_sheets_export.get_google_sheets_service')
    async def test_export_range_unsupported_format(self, mock_get_service, mock_context):
        with patch('tools.google_sheets_export.get_google_sheets_service') as mock_get_service:
            mock_service = Mock()
            mock_get_service.return_value = mock_service
            
            mock_response = {'values': [['A', 'B'], ['1', '2']]}
            mock_service.spreadsheets().values().get().execute.return_value = mock_response
            
            params = {
                'spreadsheet_id': '1ABC123',
                'range_name': 'Sheet1!A1:B2',
                'format': 'xml',
                'output_file': 'output.xml'
            }
            result = await sheets_export_range.handle(mock_context, params)
            
            action_result = await result.action()
            assert 'Unsupported format: xml' in action_result.content[0]['text']

    @pytest.mark.asyncio
    @patch('tools.google_sheets_export.get_google_sheets_service')
    async def test_create_from_csv(self, mock_get_service, mock_context, temp_dir):
        csv_file = os.path.join(temp_dir, 'data.csv')
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Product', 'Price', 'Stock'])
            writer.writerow(['Laptop', '999', '50'])
            writer.writerow(['Mouse', '25', '100'])
        
        assert os.path.exists(csv_file), f"CSV file not created at {csv_file}"
        
        with patch('tools.google_sheets_export.get_google_sheets_service') as mock_get_service:
            mock_service = Mock()
            mock_get_service.return_value = mock_service
            
            mock_create_response = {
                'spreadsheetId': '1NEW123',
                'properties': {'title': 'Product Data'}
            }
            mock_service.spreadsheets().create().execute.return_value = mock_create_response
            mock_service.spreadsheets().values().update().execute.return_value = {}
            
            params = {
                'csv_file': csv_file,
                'spreadsheet_title': 'Product Data',
                'sheet_name': 'Products'
            }
            result = await sheets_create_from_csv.handle(mock_context, params)
            
            action_result = await result.action()
            assert 'Created spreadsheet from CSV: Product Data' in action_result.content[0]['text']

    @pytest.mark.asyncio
    @patch('tools.google_sheets_export.get_google_sheets_service')
    @patch('tools.google_sheets_export.get_google_drive_service')
    async def test_backup_spreadsheet(self, mock_get_drive, mock_get_sheets, mock_context, temp_dir):
        mock_sheets_service = Mock()
        mock_drive_service = Mock()
        mock_get_sheets.return_value = mock_sheets_service
        mock_get_drive.return_value = mock_drive_service
        
        mock_sheets_service.spreadsheets().get().execute.return_value = {
            'properties': {'title': 'Test Spreadsheet'}
        }
        
        with patch('tools.google_sheets_export.MediaIoBaseDownload') as mock_download_class:
            mock_download_instance = Mock()
            mock_download_class.return_value = mock_download_instance
            mock_download_instance.next_chunk.side_effect = [(None, False), (None, True)]
            
            with patch('tools.google_sheets_export.io.BytesIO') as mock_bytesio:
                def get_value_side_effect():
                    return b'test,data\n1,2'
                mock_fh = Mock()
                mock_fh.getvalue = get_value_side_effect
                mock_bytesio.return_value = mock_fh
                
                with patch('builtins.open', mock_open()):
                    params = {
                        'spreadsheet_id': '1ABC123',
                        'backup_dir': temp_dir,
                        'include_metadata': True
                    }
                    result = await sheets_backup_spreadsheet.handle(mock_context, params)
                    
                    action_result = await result.action()
                    assert 'Backup completed for spreadsheet: Test Spreadsheet' in action_result.content[0]['text']

    @pytest.mark.asyncio
    @patch('tools.google_sheets_export.get_google_sheets_service')
    async def test_create_from_csv_file_not_found(self, mock_get_service, mock_context):
        params = {
            'csv_file': 'nonexistent.csv',
            'spreadsheet_title': 'Test'
        }
        result = await sheets_create_from_csv.handle(mock_context, params)
        
        action_result = await result.action()
        assert 'CSV file not found' in action_result.content[0]['text']

    @pytest.mark.asyncio
    @patch('tools.google_sheets_export.get_google_drive_service')
    async def test_export_sheet_error(self, mock_get_service, mock_context):
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        
        from googleapiclient.errors import HttpError
        import json
        mock_error = HttpError(
            resp=Mock(status=404),
            content=json.dumps({'error': {'message': 'Not Found'}}).encode()
        )
        mock_service.files().export_media.side_effect = mock_error
        
        params = {
            'spreadsheet_id': '1ABC123',
            'format': 'csv',
            'output_file': 'output.csv'
        }
        result = await sheets_export_sheet.handle(mock_context, params)
        
        action_result = await result.action()
        assert 'Error exporting sheet' in action_result.content[0]['text']

    @pytest.mark.asyncio
    @patch('tools.google_sheets_export.get_google_sheets_service')
    async def test_import_csv_error(self, mock_get_service, mock_context, temp_dir):
        mock_service = Mock()
        mock_get_service.return_value = mock_service
        
        from googleapiclient.errors import HttpError
        import json
        mock_error = HttpError(
            resp=Mock(status=403),
            content=json.dumps({'error': {'message': 'Forbidden'}}).encode()
        )
        mock_service.spreadsheets().values().update().execute.side_effect = mock_error
        
        csv_file = os.path.join(temp_dir, 'test.csv')
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['A', 'B'])
        
        params = {
            'spreadsheet_id': '1ABC123',
            'csv_file': csv_file
        }
        result = await sheets_import_csv.handle(mock_context, params)
        
        action_result = await result.action()
        assert 'Error importing CSV' in action_result.content[0]['text'] 
