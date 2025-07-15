import asyncio
import json
import os
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List, AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock, patch, Mock

import pytest
import pytest_asyncio

import sys
from pathlib import Path

# Add the parent directory to the path so we can import from the main package
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import FullConfig, get_default_config, resolve_config
from context import ServerContext
from core.browser_context_factory import BrowserContextManager
from tools.registry import EnhancedToolRegistry


class TestServer:

    def __init__(self, port: int = 8080):
        self.port = port
        self.PREFIX = f"http://localhost:{port}"
        self.HELLO_WORLD = f"{self.PREFIX}/hello"
        self._content: Dict[str, tuple] = {}

    def set_content(self, path: str, content: str, content_type: str = "text/html"):
        self._content[path] = (content, content_type)

    def get_content(self, path: str) -> tuple:
        return self._content.get(path, ("<h1>Not Found</h1>", "text/html"))

    def reset(self):
        self._content.clear()
        self.set_content(
            "/hello",
            """
            <html>
                <head><title>Title</title></head>
                <body>Hello, world!</body>
            </html>
        """,
        )


class MockBrowserContext:

    def __init__(self):
        self.pages = []
        self.closed = False

    async def new_page(self):
        page = MockPage()
        self.pages.append(page)
        return page

    async def close(self):
        self.closed = True
        for page in self.pages:
            await page.close()


class MockPage:

    def __init__(self):
        self.url = "about:blank"
        self._title = ""
        self._content = ""
        self.closed = False
        self._console_messages = []

    async def goto(self, url: str):
        self.url = url

    async def title(self) -> str:
        return self._title

    async def content(self) -> str:
        return self._content

    async def close(self):
        self.closed = True

    def on(self, event: str, handler):
        pass

    async def screenshot(self, **kwargs):
        return b"fake_screenshot_data"

    async def evaluate(self, script: str):
        return None


@pytest.fixture
def server() -> TestServer:
    test_server = TestServer()
    test_server.reset()
    return test_server


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


@pytest.fixture
def config_file(temp_dir: Path) -> Path:
    config_data = {
        "browser": {"browserName": "chromium", "headless": True},
        "server": {"port": 3000, "host": "localhost"},
    }
    config_path = temp_dir / "test_config.json"
    with open(config_path, "w") as f:
        json.dump(config_data, f, indent=2)
    return config_path


@pytest.fixture
def default_config() -> FullConfig:
    return get_default_config()


@pytest.fixture
def mock_browser_context() -> MockBrowserContext:
    return MockBrowserContext()


@pytest.fixture
def mock_page() -> MockPage:
    return MockPage()


@pytest_asyncio.fixture
async def context(default_config: FullConfig) -> AsyncGenerator[ServerContext, None]:
    from config.settings import config_to_settings

    settings = config_to_settings(default_config)

    with patch("playwright.async_api.async_playwright") as mock_playwright:
        mock_playwright_instance = AsyncMock()
        mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance

        mock_browser = AsyncMock()
        mock_playwright_instance.chromium.launch.return_value = mock_browser

        mock_browser_context = MockBrowserContext()
        mock_browser.new_context.return_value = mock_browser_context

        context = ServerContext(settings)
        yield context

        await context.close()


@pytest_asyncio.fixture
async def tool_registry(context: ServerContext) -> EnhancedToolRegistry:
    return context.tool_registry


def assert_text_content(response: Dict[str, Any], expected: str):
    if "content" in response:
        for item in response["content"]:
            if item.get("type") == "text" and expected in item.get("text", ""):
                return
    raise AssertionError(f"Expected text '{expected}' not found in response")


def assert_contains_text_content(response: Dict[str, Any], expected: List[str]):
    if "content" in response:
        text_content = ""
        for item in response["content"]:
            if item.get("type") == "text":
                text_content += item.get("text", "")

        for expected_text in expected:
            if expected_text not in text_content:
                raise AssertionError(
                    f"Expected text '{expected_text}' not found in response"
                )
    else:
        raise AssertionError("No content found in response")


def pytest_configure(config):
    config.addinivalue_line("markers", "asyncio: mark test as async")
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "unit: mark test as unit test")


def pytest_collection_modifyitems(config, items):
    for item in items:
        if asyncio.iscoroutinefunction(item.function):
            item.add_marker(pytest.mark.asyncio)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_google_credentials():
    with patch('google.oauth2.service_account.Credentials.from_service_account_file') as mock_creds:
        mock_creds.return_value = Mock()
        yield mock_creds


@pytest.fixture
def mock_build_service():
    with patch('googleapiclient.discovery.build') as mock_build:
        yield mock_build


# Disabled autouse fixture that may interfere with file operations
# @pytest.fixture(autouse=True)
def mock_service_account_file():
    mock_service_data = {
        "type": "service_account",
        "project_id": "test-project",
        "private_key_id": "test-key-id",
        "private_key": "-----BEGIN PRIVATE KEY-----\nMOCK_KEY\n-----END PRIVATE KEY-----",
        "client_email": "test@test-project.iam.gserviceaccount.com",
        "client_id": "123456789",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token"
    }
    
    with patch('builtins.open', mock_open_service_file(mock_service_data)):
        with patch('os.path.exists', return_value=True):
            yield mock_service_data


def mock_open_service_file(mock_data):
    import json
    from unittest.mock import mock_open
    
    def side_effect(*args, **kwargs):
        if 'service-account.json' in str(args[0]):
            return mock_open(read_data=json.dumps(mock_data))()
        return mock_open()(*args, **kwargs)
    
    return side_effect


@pytest.fixture
def sample_spreadsheet_data():
    return {
        'spreadsheetId': '1ABC123DEF456',
        'properties': {
            'title': 'Test Spreadsheet'
        },
        'sheets': [
            {
                'properties': {
                    'sheetId': 0,
                    'title': 'Sheet1',
                    'gridProperties': {
                        'rowCount': 1000,
                        'columnCount': 26
                    }
                }
            }
        ]
    }


@pytest.fixture
def sample_csv_data():
    return [
        ['Name', 'Age', 'City'],
        ['John Doe', '25', 'New York'],
        ['Jane Smith', '30', 'Los Angeles'],
        ['Bob Johnson', '35', 'Chicago']
    ]


@pytest.fixture
def mock_http_error():
    from googleapiclient.errors import HttpError
    
    def create_error(status_code, message):
        resp = Mock()
        resp.status = status_code
        return HttpError(resp=resp, content=message.encode())
    
    return create_error


@pytest.fixture
def google_sheets_service_mock():
    service = Mock()
    
    service.spreadsheets.return_value = Mock()
    service.spreadsheets().create.return_value = Mock()
    service.spreadsheets().get.return_value = Mock()
    service.spreadsheets().batchUpdate.return_value = Mock()
    service.spreadsheets().values.return_value = Mock()
    service.spreadsheets().values().get.return_value = Mock()
    service.spreadsheets().values().update.return_value = Mock()
    service.spreadsheets().values().append.return_value = Mock()
    service.spreadsheets().values().clear.return_value = Mock()
    
    return service


@pytest.fixture
def google_drive_service_mock():
    service = Mock()
    
    service.files.return_value = Mock()
    service.files().list.return_value = Mock()
    service.files().export_media.return_value = Mock()
    service.permissions.return_value = Mock()
    service.permissions().create.return_value = Mock()
    
    return service


# Disabled autouse fixture to allow manual mocking in tests
# @pytest.fixture(autouse=True)
def mock_all_google_services(google_sheets_service_mock, google_drive_service_mock):
    with patch('tools.google_sheets.get_google_sheets_service', return_value=google_sheets_service_mock):
        with patch('tools.google_sheets.get_google_drive_service', return_value=google_drive_service_mock):
            yield
