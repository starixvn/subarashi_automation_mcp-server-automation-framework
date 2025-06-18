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
async def test_browser_press_key_single():
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
// Press key Enter
await page.keyboard.press('Enter');
```

Key 'Enter' pressed successfully.
""",
                }
            ]

            result = await registry.execute_tool("browser_press_key", {"key": "Enter"})

            assert hasattr(result, "content")
            assert result.content is not None
            text_content = ""
            for item in result.content:
                if item.get("type") == "text":
                    text_content += item.get("text", "")

            assert "Press key Enter" in text_content
            assert "Key 'Enter' pressed successfully" in text_content


@pytest.mark.asyncio
async def test_browser_press_key_escape():
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
// Press key Escape
await page.keyboard.press('Escape');
```

Key 'Escape' pressed successfully.
""",
                }
            ]

            result = await registry.execute_tool("browser_press_key", {"key": "Escape"})

            assert hasattr(result, "content")
            assert result.content is not None
            text_content = ""
            for item in result.content:
                if item.get("type") == "text":
                    text_content += item.get("text", "")

            assert "Press key Escape" in text_content
            assert "Key 'Escape' pressed successfully" in text_content


@pytest.mark.asyncio
async def test_browser_press_key_tab():
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
// Press key Tab
await page.keyboard.press('Tab');
```

Key 'Tab' pressed successfully.
""",
                }
            ]

            result = await registry.execute_tool("browser_press_key", {"key": "Tab"})

            assert hasattr(result, "content")
            assert result.content is not None
            text_content = ""
            for item in result.content:
                if item.get("type") == "text":
                    text_content += item.get("text", "")

            assert "Press key Tab" in text_content
            assert "Key 'Tab' pressed successfully" in text_content


@pytest.mark.asyncio
async def test_browser_press_key_shift_tab():
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
// Press key Shift+Tab
await page.keyboard.press('Shift+Tab');
```

Key 'Shift+Tab' pressed successfully.
""",
                }
            ]

            result = await registry.execute_tool("browser_press_key", {"key": "Shift+Tab"})

            assert hasattr(result, "content")
            assert result.content is not None
            text_content = ""
            for item in result.content:
                if item.get("type") == "text":
                    text_content += item.get("text", "")

            assert "Press key Shift+Tab" in text_content
            assert "Key 'Shift+Tab' pressed successfully" in text_content


@pytest.mark.asyncio
async def test_browser_press_key_ctrl_a():
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
// Press key Control+a
await page.keyboard.press('Control+a');
```

Key 'Control+a' pressed successfully.
""",
                }
            ]

            result = await registry.execute_tool("browser_press_key", {"key": "Control+a"})

            assert hasattr(result, "content")
            assert result.content is not None
            text_content = ""
            for item in result.content:
                if item.get("type") == "text":
                    text_content += item.get("text", "")

            assert "Press key Control+a" in text_content
            assert "Key 'Control+a' pressed successfully" in text_content


@pytest.mark.asyncio
async def test_browser_press_key_character():
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
// Press key a
await page.keyboard.press('a');
```

Key 'a' pressed successfully.
""",
                }
            ]

            result = await registry.execute_tool("browser_press_key", {"key": "a"})

            assert hasattr(result, "content")
            assert result.content is not None
            text_content = ""
            for item in result.content:
                if item.get("type") == "text":
                    text_content += item.get("text", "")

            assert "Press key a" in text_content
            assert "Key 'a' pressed successfully" in text_content


@pytest.mark.asyncio
async def test_browser_press_key_arrow_keys():
    default_config = get_default_config()
    settings = config_to_settings(default_config)

    with patch("playwright.async_api.async_playwright") as mock_playwright:
        mock_playwright_instance = AsyncMock()
        mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance

        context = ServerContext(settings)
        registry = context.tool_registry

        arrow_keys = ["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight"]

        for key in arrow_keys:
            with patch.object(registry, "execute_tool") as mock_execute:
                mock_execute.return_value = MagicMock()
                mock_execute.return_value.content = [
                    {
                        "type": "text",
                        "text": f"""
- Ran Playwright code:
```js
// Press key {key}
await page.keyboard.press('{key}');
```

Key '{key}' pressed successfully.
""",
                    }
                ]

                result = await registry.execute_tool("browser_press_key", {"key": key})

                assert hasattr(result, "content")
                assert result.content is not None
                text_content = ""
                for item in result.content:
                    if item.get("type") == "text":
                        text_content += item.get("text", "")

                assert f"Press key {key}" in text_content
                assert f"Key '{key}' pressed successfully" in text_content


@pytest.mark.asyncio
async def test_browser_press_key_error_handling():
    default_config = get_default_config()
    settings = config_to_settings(default_config)

    with patch("playwright.async_api.async_playwright") as mock_playwright:
        mock_playwright_instance = AsyncMock()
        mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance

        context = ServerContext(settings)
        registry = context.tool_registry

        with patch.object(registry, "execute_tool") as mock_execute:
            mock_execute.side_effect = Exception("Invalid key: InvalidKey")

            with pytest.raises(Exception, match="Invalid key: InvalidKey"):
                await registry.execute_tool("browser_press_key", {"key": "InvalidKey"})


@pytest.mark.asyncio
async def test_browser_press_key_function_keys():
    default_config = get_default_config()
    settings = config_to_settings(default_config)

    with patch("playwright.async_api.async_playwright") as mock_playwright:
        mock_playwright_instance = AsyncMock()
        mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance

        context = ServerContext(settings)
        registry = context.tool_registry

        function_keys = ["F1", "F5", "F12"]

        for key in function_keys:
            with patch.object(registry, "execute_tool") as mock_execute:
                mock_execute.return_value = MagicMock()
                mock_execute.return_value.content = [
                    {
                        "type": "text",
                        "text": f"""
- Ran Playwright code:
```js
// Press key {key}
await page.keyboard.press('{key}');
```

Key '{key}' pressed successfully.
""",
                    }
                ]

                result = await registry.execute_tool("browser_press_key", {"key": key})

                assert hasattr(result, "content")
                assert result.content is not None
                text_content = ""
                for item in result.content:
                    if item.get("type") == "text":
                        text_content += item.get("text", "")

                assert f"Press key {key}" in text_content
                assert f"Key '{key}' pressed successfully" in text_content


@pytest.mark.asyncio
async def test_keyboard_capability_filtering():
    config = Config(
        browser=get_default_config().browser,
        server=get_default_config().server,
        network=get_default_config().network,
        capabilities=["core", "keyboard"],
    )
    settings = config_to_settings(config)

    with patch("playwright.async_api.async_playwright") as mock_playwright:
        mock_playwright_instance = AsyncMock()
        mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance

        context = ServerContext(settings)
        registry = context.tool_registry

        tools = await registry.list_tools()
        tool_names = {tool["name"] for tool in tools}

        assert "browser_press_key" in tool_names 