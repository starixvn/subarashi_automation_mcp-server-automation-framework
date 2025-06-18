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
async def test_browser_wait_for_time():
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
// Wait for 3 seconds
await page.waitForTimeout(3000);
```

Waited for 3 seconds successfully.
""",
                }
            ]

            result = await registry.execute_tool("browser_wait_for", {"time": 3})

            assert hasattr(result, "content")
            assert result.content is not None
            text_content = ""
            for item in result.content:
                if item.get("type") == "text":
                    text_content += item.get("text", "")

            assert "Wait for 3 seconds" in text_content
            assert "Waited for 3 seconds successfully" in text_content


@pytest.mark.asyncio
async def test_browser_wait_for_text():
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
// Wait for text "Loading complete" to appear
await page.waitForSelector('text=Loading complete', { timeout: 30000 });
```

Text "Loading complete" appeared successfully.
""",
                }
            ]

            result = await registry.execute_tool(
                "browser_wait_for", {"text": "Loading complete"}
            )

            assert hasattr(result, "content")
            assert result.content is not None
            text_content = ""
            for item in result.content:
                if item.get("type") == "text":
                    text_content += item.get("text", "")

            assert "Wait for text \"Loading complete\"" in text_content
            assert "Text \"Loading complete\" appeared successfully" in text_content


@pytest.mark.asyncio
async def test_browser_wait_for_text_gone():
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
// Wait for text "Loading..." to disappear
await page.waitForSelector('text=Loading...', { state: 'detached', timeout: 30000 });
```

Text "Loading..." disappeared successfully.
""",
                }
            ]

            result = await registry.execute_tool(
                "browser_wait_for", {"text_gone": "Loading..."}
            )

            assert hasattr(result, "content")
            assert result.content is not None
            text_content = ""
            for item in result.content:
                if item.get("type") == "text":
                    text_content += item.get("text", "")

            assert "Wait for text \"Loading...\" to disappear" in text_content
            assert "Text \"Loading...\" disappeared successfully" in text_content


@pytest.mark.asyncio
async def test_browser_wait_for_selector_visible():
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
// Wait for selector .modal-dialog to appear (timeout: 10 seconds)
await page.waitForSelector('.modal-dialog', { timeout: 10000 });
```

Element with selector '.modal-dialog' appeared successfully.
""",
                }
            ]

            result = await registry.execute_tool(
                "browser_wait_for_selector",
                {"selector": ".modal-dialog", "timeout": 10},
            )

            assert hasattr(result, "content")
            assert result.content is not None
            text_content = ""
            for item in result.content:
                if item.get("type") == "text":
                    text_content += item.get("text", "")

            assert "Wait for selector .modal-dialog to appear" in text_content
            assert "timeout: 10 seconds" in text_content
            assert "Element with selector '.modal-dialog' appeared successfully" in text_content


@pytest.mark.asyncio
async def test_browser_wait_for_selector_default_timeout():
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
// Wait for selector button.submit to appear (timeout: 10 seconds)
await page.waitForSelector('button.submit', { timeout: 10000 });
```

Element with selector 'button.submit' appeared successfully.
""",
                }
            ]

            result = await registry.execute_tool(
                "browser_wait_for_selector", {"selector": "button.submit"}
            )

            assert hasattr(result, "content")
            assert result.content is not None
            text_content = ""
            for item in result.content:
                if item.get("type") == "text":
                    text_content += item.get("text", "")

            assert "Wait for selector button.submit to appear" in text_content
            assert "timeout: 10 seconds" in text_content


@pytest.mark.asyncio
async def test_browser_wait_for_multiple_conditions():
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
// Wait for text "Data loaded" to appear and time 2 seconds
await Promise.all([
  page.waitForSelector('text=Data loaded', { timeout: 30000 }),
  page.waitForTimeout(2000)
]);
```

Multiple conditions met:
- Text "Data loaded" appeared
- Waited for 2 seconds
""",
                }
            ]

            result = await registry.execute_tool(
                "browser_wait_for", {"text": "Data loaded", "time": 2}
            )

            assert hasattr(result, "content")
            assert result.content is not None
            text_content = ""
            for item in result.content:
                if item.get("type") == "text":
                    text_content += item.get("text", "")

            assert "Multiple conditions met" in text_content
            assert "Text \"Data loaded\" appeared" in text_content
            assert "Waited for 2 seconds" in text_content


@pytest.mark.asyncio
async def test_browser_wait_for_timeout_error():
    default_config = get_default_config()
    settings = config_to_settings(default_config)

    with patch("playwright.async_api.async_playwright") as mock_playwright:
        mock_playwright_instance = AsyncMock()
        mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance

        context = ServerContext(settings)
        registry = context.tool_registry

        with patch.object(registry, "execute_tool") as mock_execute:
            mock_execute.side_effect = Exception(
                "Timeout: Element with selector '#non-existent' not found"
            )

            with pytest.raises(
                Exception, match="Timeout: Element with selector '#non-existent' not found"
            ):
                await registry.execute_tool(
                    "browser_wait_for_selector",
                    {"selector": "#non-existent", "timeout": 1},
                )


@pytest.mark.asyncio
async def test_browser_wait_for_text_timeout():
    default_config = get_default_config()
    settings = config_to_settings(default_config)

    with patch("playwright.async_api.async_playwright") as mock_playwright:
        mock_playwright_instance = AsyncMock()
        mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance

        context = ServerContext(settings)
        registry = context.tool_registry

        with patch.object(registry, "execute_tool") as mock_execute:
            mock_execute.side_effect = Exception(
                "Timeout: Text 'Never appears' not found"
            )

            with pytest.raises(Exception, match="Timeout: Text 'Never appears' not found"):
                await registry.execute_tool(
                    "browser_wait_for", {"text": "Never appears"}
                )


@pytest.mark.asyncio
async def test_browser_wait_for_selector_states():
    default_config = get_default_config()
    settings = config_to_settings(default_config)

    with patch("playwright.async_api.async_playwright") as mock_playwright:
        mock_playwright_instance = AsyncMock()
        mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance

        context = ServerContext(settings)
        registry = context.tool_registry

        states = ["visible", "hidden", "attached", "detached"]

        for state in states:
            with patch.object(registry, "execute_tool") as mock_execute:
                mock_execute.return_value = MagicMock()
                mock_execute.return_value.content = [
                    {
                        "type": "text",
                        "text": f"""
- Ran Playwright code:
```js
// Wait for selector .element to be {state} (timeout: 10 seconds)
await page.waitForSelector('.element', {{ state: '{state}', timeout: 10000 }});
```

Element with selector '.element' is now {state}.
""",
                    }
                ]

                result = await registry.execute_tool(
                    "browser_wait_for_selector",
                    {"selector": ".element", "state": state, "timeout": 10},
                )

                assert hasattr(result, "content")
                assert result.content is not None
                text_content = ""
                for item in result.content:
                    if item.get("type") == "text":
                        text_content += item.get("text", "")

                assert f"Wait for selector .element to be {state}" in text_content
                assert f"Element with selector '.element' is now {state}" in text_content


@pytest.mark.asyncio
async def test_browser_wait_for_complex_selectors():
    default_config = get_default_config()
    settings = config_to_settings(default_config)

    with patch("playwright.async_api.async_playwright") as mock_playwright:
        mock_playwright_instance = AsyncMock()
        mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance

        context = ServerContext(settings)
        registry = context.tool_registry

        complex_selectors = [
            'div[data-testid="loading-spinner"]',
            'button:has-text("Submit"):visible',
            '.modal.open .close-button',
            'input[type="email"]:focus',
        ]

        for selector in complex_selectors:
            with patch.object(registry, "execute_tool") as mock_execute:
                mock_execute.return_value = MagicMock()
                mock_execute.return_value.content = [
                    {
                        "type": "text",
                        "text": f"""
- Ran Playwright code:
```js
// Wait for selector {selector} to appear (timeout: 10 seconds)
await page.waitForSelector('{selector}', {{ timeout: 10000 }});
```

Element with selector '{selector}' appeared successfully.
""",
                    }
                ]

                result = await registry.execute_tool(
                    "browser_wait_for_selector", {"selector": selector}
                )

                assert hasattr(result, "content")
                assert result.content is not None
                text_content = ""
                for item in result.content:
                    if item.get("type") == "text":
                        text_content += item.get("text", "")

                assert f"Wait for selector {selector} to appear" in text_content
                assert f"Element with selector '{selector}' appeared successfully" in text_content


@pytest.mark.asyncio
async def test_wait_capability_filtering():
    config = Config(
        browser=get_default_config().browser,
        server=get_default_config().server,
        network=get_default_config().network,
        capabilities=["core", "wait"],
    )
    settings = config_to_settings(config)

    with patch("playwright.async_api.async_playwright") as mock_playwright:
        mock_playwright_instance = AsyncMock()
        mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance

        context = ServerContext(settings)
        registry = context.tool_registry

        tools = await registry.list_tools()
        tool_names = {tool["name"] for tool in tools}

        assert "browser_wait_for" in tool_names
        assert "browser_wait_for_selector" in tool_names 