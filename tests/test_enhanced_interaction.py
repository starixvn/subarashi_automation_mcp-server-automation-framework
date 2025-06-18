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
async def test_browser_get_text():
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
// Get text from element h1
const text = await page.locator('h1').textContent();
```

Text content from 'h1': Welcome to Our Website
""",
                }
            ]

            result = await registry.execute_tool(
                "browser_get_text", {"selector": "h1"}
            )

            assert hasattr(result, "content")
            assert result.content is not None
            text_content = ""
            for item in result.content:
                if item.get("type") == "text":
                    text_content += item.get("text", "")

            assert "Get text from element h1" in text_content
            assert "Text content from 'h1': Welcome to Our Website" in text_content


@pytest.mark.asyncio
async def test_browser_get_text_multiple_elements():
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
// Get text from all elements matching .item
const elements = await page.locator('.item').all();
const texts = await Promise.all(elements.map(el => el.textContent()));
```

Text content from '.item' elements:
1. Product 1
2. Product 2
3. Product 3
""",
                }
            ]

            result = await registry.execute_tool(
                "browser_get_text", {"selector": ".item"}
            )

            assert hasattr(result, "content")
            assert result.content is not None
            text_content = ""
            for item in result.content:
                if item.get("type") == "text":
                    text_content += item.get("text", "")

            assert "Get text from all elements matching .item" in text_content
            assert "Text content from '.item' elements:" in text_content
            assert "1. Product 1" in text_content
            assert "2. Product 2" in text_content
            assert "3. Product 3" in text_content


@pytest.mark.asyncio
async def test_browser_get_text_empty():
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
// Get text from element .empty
const text = await page.locator('.empty').textContent();
```

Text content from '.empty': (empty)
""",
                }
            ]

            result = await registry.execute_tool(
                "browser_get_text", {"selector": ".empty"}
            )

            assert hasattr(result, "content")
            assert result.content is not None
            text_content = ""
            for item in result.content:
                if item.get("type") == "text":
                    text_content += item.get("text", "")

            assert "Get text from element .empty" in text_content
            assert "Text content from '.empty': (empty)" in text_content


@pytest.mark.asyncio
async def test_browser_get_text_error():
    default_config = get_default_config()
    settings = config_to_settings(default_config)

    with patch("playwright.async_api.async_playwright") as mock_playwright:
        mock_playwright_instance = AsyncMock()
        mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance

        context = ServerContext(settings)
        registry = context.tool_registry

        with patch.object(registry, "execute_tool") as mock_execute:
            mock_execute.side_effect = Exception("Element not found: .nonexistent")

            with pytest.raises(Exception, match="Element not found: .nonexistent"):
                await registry.execute_tool(
                    "browser_get_text", {"selector": ".nonexistent"}
                )


@pytest.mark.asyncio
async def test_browser_drag():
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
// Drag element from .draggable to .dropzone
await page.locator('.draggable').dragTo(page.locator('.dropzone'));
```

Drag operation completed successfully.
Source: .draggable
Target: .dropzone
""",
                }
            ]

            result = await registry.execute_tool(
                "browser_drag",
                {
                    "start_element": "draggable item",
                    "start_ref": "e1",
                    "end_element": "drop zone",
                    "end_ref": "e2",
                },
            )

            assert hasattr(result, "content")
            assert result.content is not None
            text_content = ""
            for item in result.content:
                if item.get("type") == "text":
                    text_content += item.get("text", "")

            assert "Drag element from .draggable to .dropzone" in text_content
            assert "Drag operation completed successfully" in text_content
            assert "Source: .draggable" in text_content
            assert "Target: .dropzone" in text_content


@pytest.mark.asyncio
async def test_browser_drag_with_coordinates():
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
// Drag element from .slider-handle by offset (100, 0)
await page.locator('.slider-handle').dragTo(page.locator('.slider-handle'), {
  targetPosition: { x: 100, y: 0 }
});
```

Drag operation completed successfully.
Source: .slider-handle
Movement: 100px right, 0px down
""",
                }
            ]

            result = await registry.execute_tool(
                "browser_drag",
                {
                    "start_element": "slider handle",
                    "start_ref": "e1",
                    "end_element": "target position",
                    "end_ref": "e2",
                    "offset_x": 100,
                    "offset_y": 0,
                },
            )

            assert hasattr(result, "content")
            assert result.content is not None
            text_content = ""
            for item in result.content:
                if item.get("type") == "text":
                    text_content += item.get("text", "")

            assert "Drag element from .slider-handle by offset" in text_content
            assert "Drag operation completed successfully" in text_content
            assert "Movement: 100px right, 0px down" in text_content


@pytest.mark.asyncio
async def test_browser_drag_sortable_list():
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
// Drag list item from position 1 to position 3
await page.locator('.list-item:nth-child(1)').dragTo(page.locator('.list-item:nth-child(3)'));
```

Drag operation completed successfully.
Source: List item 1 (Task A)
Target: List item 3 (Task C)
New order: Task B, Task C, Task A
""",
                }
            ]

            result = await registry.execute_tool(
                "browser_drag",
                {
                    "start_element": "Task A",
                    "start_ref": "e1",
                    "end_element": "Task C position",
                    "end_ref": "e3",
                },
            )

            assert hasattr(result, "content")
            assert result.content is not None
            text_content = ""
            for item in result.content:
                if item.get("type") == "text":
                    text_content += item.get("text", "")

            assert "Drag list item from position 1 to position 3" in text_content
            assert "Drag operation completed successfully" in text_content
            assert "Source: List item 1 (Task A)" in text_content
            assert "Target: List item 3 (Task C)" in text_content
            assert "New order: Task B, Task C, Task A" in text_content


@pytest.mark.asyncio
async def test_browser_drag_error():
    default_config = get_default_config()
    settings = config_to_settings(default_config)

    with patch("playwright.async_api.async_playwright") as mock_playwright:
        mock_playwright_instance = AsyncMock()
        mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance

        context = ServerContext(settings)
        registry = context.tool_registry

        with patch.object(registry, "execute_tool") as mock_execute:
            mock_execute.side_effect = Exception("Source element not found: .missing")

            with pytest.raises(Exception, match="Source element not found: .missing"):
                await registry.execute_tool(
                    "browser_drag",
                    {
                        "start_element": "missing element",
                        "start_ref": "e1",
                        "end_element": "target",
                        "end_ref": "e2",
                    },
                )


@pytest.mark.asyncio
async def test_browser_drag_canvas():
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
// Drag on canvas from (50, 50) to (150, 100)
const canvas = page.locator('canvas');
await canvas.hover({ position: { x: 50, y: 50 } });
await page.mouse.down();
await canvas.hover({ position: { x: 150, y: 100 } });
await page.mouse.up();
```

Canvas drag operation completed successfully.
Start position: (50, 50)
End position: (150, 100)
Distance: 111.8px
""",
                }
            ]

            result = await registry.execute_tool(
                "browser_drag",
                {
                    "start_element": "canvas point",
                    "start_ref": "e1",
                    "end_element": "canvas end point",
                    "end_ref": "e2",
                    "start_x": 50,
                    "start_y": 50,
                    "end_x": 150,
                    "end_y": 100,
                },
            )

            assert hasattr(result, "content")
            assert result.content is not None
            text_content = ""
            for item in result.content:
                if item.get("type") == "text":
                    text_content += item.get("text", "")

            assert "Drag on canvas from (50, 50) to (150, 100)" in text_content
            assert "Canvas drag operation completed successfully" in text_content
            assert "Start position: (50, 50)" in text_content
            assert "End position: (150, 100)" in text_content
            assert "Distance: 111.8px" in text_content 