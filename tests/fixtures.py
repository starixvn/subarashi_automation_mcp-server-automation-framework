import asyncio
import json
import os
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, List, AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from mcp.client.session import ClientSession
from mcp import StdioServerParameters
from mcp.client.stdio import stdio_client

from config.settings import (
    FullConfig,
    get_default_config,
    resolve_config,
    config_to_settings,
)
from context import ServerContext
from core.browser_context_factory import BrowserContextManager
from core.registry import EnhancedToolRegistry
from server import create_server


class TestServer:

    def __init__(self, port: int = 8080):
        self.port = port
        self.prefix = f"http://localhost:{port}"
        self.hello_world = f"{self.prefix}/hello"
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
        self.title = ""
        self.content = ""
        self.closed = False
        self._console_messages = []

    async def goto(self, url: str):
        self.url = url

    async def title(self) -> str:
        return self.title

    async def content(self) -> str:
        return self.content

    async def close(self):
        self.closed = True

    def on(self, event: str, handler):
        pass

    async def screenshot(self, **kwargs):
        return b"fake_screenshot_data"

    async def evaluate(self, script: str):
        return None


@pytest.fixture
def test_server() -> TestServer:
    server = TestServer()
    server.reset()
    return server


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
    return resolve_config(get_default_config())


@pytest.fixture
def mock_browser_context() -> MockBrowserContext:
    return MockBrowserContext()


@pytest.fixture
def mock_page() -> MockPage:
    return MockPage()


@pytest_asyncio.fixture
async def context(default_config: FullConfig) -> AsyncGenerator[ServerContext, None]:
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


@pytest_asyncio.fixture
async def mcp_client(default_config: FullConfig) -> AsyncGenerator[ClientSession, None]:
    server = create_server(default_config)

    with patch("mcp.client.stdio.stdio_client") as mock_stdio:
        mock_session = AsyncMock(spec=ClientSession)
        mock_stdio.return_value.__aenter__.return_value = mock_session

        mock_session.list_tools.return_value = {
            "tools": [
                {"name": "browser_navigate", "description": "Navigate to URL"},
                {"name": "browser_click", "description": "Click element"},
                {"name": "browser_type", "description": "Type text"},
            ]
        }

        mock_session.call_tool.return_value = {
            "content": [{"type": "text", "text": "Tool executed successfully"}]
        }

        yield mock_session


class TestOptions:

    def __init__(
        self,
        browser: str = "chromium",
        headless: bool = True,
        mode: Optional[str] = None,
    ):
        self.browser = browser
        self.headless = headless
        self.mode = mode


@pytest.fixture
def test_options() -> TestOptions:
    return TestOptions()


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
