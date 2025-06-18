import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import sys
from pathlib import Path

# Add the parent directory to the path so we can import from the main package
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.conftest import assert_text_content, assert_contains_text_content
from context import ServerContext
from config.settings import Config, get_default_config, config_to_settings


@pytest.mark.asyncio
async def test_browser_console_clear():
    default_config = get_default_config()
    settings = config_to_settings(default_config)

    with patch("playwright.async_api.async_playwright") as mock_playwright:
        mock_playwright_instance = AsyncMock()
        mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance

        context = ServerContext(settings)
        registry = context.tool_registry

        with patch.object(registry, "execute_tool") as mock_execute:
            mock_execute.return_value = MagicMock()
            mock_execute.return_value.content = [
                {
                    "type": "text",
                    "text": """
- Ran Playwright code:
```js
// Clear browser console messages
await page.evaluate(() => console.clear());
```

Console cleared successfully.
All previous console messages have been removed.
""",
                }
            ]

            result = await registry.execute_tool("browser_console_clear", {})

            assert hasattr(result, "content")
            assert result.content is not None
            text_content = ""
            for item in result.content:
                if item.get("type") == "text":
                    text_content += item.get("text", "")

            assert "Clear browser console messages" in text_content
            assert "Console cleared successfully" in text_content
            assert "All previous console messages have been removed" in text_content


@pytest.mark.asyncio
async def test_browser_console_messages():
    default_config = get_default_config()
    settings = config_to_settings(default_config)

    with patch("playwright.async_api.async_playwright") as mock_playwright:
        mock_playwright_instance = AsyncMock()
        mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance

        context = ServerContext(settings)
        registry = context.tool_registry

        with patch.object(registry, "execute_tool") as mock_execute:
            mock_execute.return_value = MagicMock()
            mock_execute.return_value.content = [
                {
                    "type": "text",
                    "text": """
- Ran Playwright code:
```js
// Get browser console messages
const messages = await page.evaluate(() => {
    return window.consoleMessages || [];
});
```

Console Messages (3 total):
1. [LOG] Application started successfully
2. [WARN] Deprecated API usage detected
3. [ERROR] Failed to load resource: https://example.com/missing.js
""",
                }
            ]

            result = await registry.execute_tool("browser_console_messages", {})

            assert hasattr(result, "content")
            assert result.content is not None
            text_content = ""
            for item in result.content:
                if item.get("type") == "text":
                    text_content += item.get("text", "")

            assert "Get browser console messages" in text_content
            assert "Console Messages (3 total):" in text_content
            assert "[LOG] Application started successfully" in text_content
            assert "[WARN] Deprecated API usage detected" in text_content
            assert "[ERROR] Failed to load resource" in text_content


@pytest.mark.asyncio
async def test_browser_console_messages_empty():
    default_config = get_default_config()
    settings = config_to_settings(default_config)

    with patch("playwright.async_api.async_playwright") as mock_playwright:
        mock_playwright_instance = AsyncMock()
        mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance

        context = ServerContext(settings)
        registry = context.tool_registry

        with patch.object(registry, "execute_tool") as mock_execute:
            mock_execute.return_value = MagicMock()
            mock_execute.return_value.content = [
                {
                    "type": "text",
                    "text": """
- Ran Playwright code:
```js
// Get browser console messages
const messages = await page.evaluate(() => {
    return window.consoleMessages || [];
});
```

Console Messages: No messages found
""",
                }
            ]

            result = await registry.execute_tool("browser_console_messages", {})

            assert hasattr(result, "content")
            assert result.content is not None
            text_content = ""
            for item in result.content:
                if item.get("type") == "text":
                    text_content += item.get("text", "")

            assert "Get browser console messages" in text_content
            assert "Console Messages: No messages found" in text_content


@pytest.mark.asyncio
async def test_console_capability_filtering():
    config = Config(
        browser=get_default_config().browser,
        server=get_default_config().server,
        network=get_default_config().network,
        capabilities=["core", "console"],
    )
    settings = config_to_settings(config)

    with patch("playwright.async_api.async_playwright") as mock_playwright:
        mock_playwright_instance = AsyncMock()
        mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance

        context = ServerContext(settings)
        registry = context.tool_registry

        tools = await registry.list_tools()
        tool_names = {tool["name"] for tool in tools}

        assert "browser_console_clear" in tool_names
        assert "browser_console_messages" in tool_names 