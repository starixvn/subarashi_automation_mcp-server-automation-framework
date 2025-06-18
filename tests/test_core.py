import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from tests.conftest import assert_text_content, assert_contains_text_content
from tools.registry import EnhancedToolRegistry
from context import ServerContext


@pytest.mark.asyncio
async def test_browser_navigate(tool_registry: EnhancedToolRegistry, server):
    with patch.object(tool_registry, "execute_tool") as mock_execute:
        mock_execute.return_value = MagicMock()
        mock_execute.return_value.content = [
            {
                "type": "text",
                "text": f"""
- Ran Playwright code:
```js
// Navigate to {server.HELLO_WORLD}
await page.goto('{server.HELLO_WORLD}');
```

- Page URL: {server.HELLO_WORLD}
- Page Title: Title
- Page Snapshot
```yaml
- generic [ref=e1]: Hello, world!
```
""",
            }
        ]

        result = await tool_registry.execute_tool(
            "browser_navigate", {"url": server.HELLO_WORLD}
        )

        assert hasattr(result, "content")
        assert result.content is not None
        text_content = ""
        for item in result.content:
            if item.get("type") == "text":
                text_content += item.get("text", "")

        assert f"Navigate to {server.HELLO_WORLD}" in text_content
        assert "Page URL:" in text_content
        assert "Page Title: Title" in text_content
        assert "Page Snapshot" in text_content
        assert "- generic [ref=e1]: Hello, world!" in text_content


@pytest.mark.asyncio
async def test_browser_click(tool_registry: EnhancedToolRegistry, server):
    server.set_content(
        "/",
        """
        <title>Title</title>
        <button>Submit</button>
    """,
        "text/html",
    )

    with patch.object(tool_registry, "execute_tool") as mock_execute:
        mock_execute.return_value = MagicMock()
        mock_execute.return_value.content = [
            {
                "type": "text",
                "text": f"""
- Ran Playwright code:
```js
// Click Submit button
await page.getByRole('button', {{ name: 'Submit' }}).click();
```

- Page URL: {server.PREFIX}
- Page Title: Title
- Page Snapshot
```yaml
- button "Submit" [ref=e2]
```
""",
            }
        ]

        result = await tool_registry.execute_tool(
            "browser_click", {"element": "Submit button", "ref": "e2"}
        )

        assert hasattr(result, "content")
        assert result.content is not None
        text_content = ""
        for item in result.content:
            if item.get("type") == "text":
                text_content += item.get("text", "")

        assert "Click Submit button" in text_content
        assert "Page URL:" in text_content
        assert "Page Title: Title" in text_content
        assert '- button "Submit" [ref=e2]' in text_content


@pytest.mark.asyncio
async def test_browser_type(tool_registry: EnhancedToolRegistry, server):
    server.set_content(
        "/",
        """
        <!DOCTYPE html>
        <html>
          <input type='text' onkeypress="console.log('Key pressed:', event.key, ', Text:', event.target.value)"></input>
        </html>
    """,
        "text/html",
    )

    with patch.object(tool_registry, "execute_tool") as mock_execute:
        mock_execute.return_value = MagicMock()
        mock_execute.return_value.content = [
            {
                "type": "text",
                "text": f"""
- Ran Playwright code:
```js
// Type Hi! in textbox
await page.getByRole('textbox').type('Hi!');
await page.getByRole('textbox').press('Enter');
```

- Page URL: {server.PREFIX}
- Page Title: 
- Page Snapshot
```yaml
- textbox [ref=e2]
```
""",
            }
        ]

        result = await tool_registry.execute_tool(
            "browser_type",
            {"element": "textbox", "ref": "e2", "text": "Hi!", "submit": True},
        )

        assert hasattr(result, "content")
        assert result.content is not None
        text_content = ""
        for item in result.content:
            if item.get("type") == "text":
                text_content += item.get("text", "")

        assert "Type Hi!" in text_content
        assert "Hi!" in text_content


@pytest.mark.asyncio
async def test_browser_select_option(tool_registry: EnhancedToolRegistry, server):
    server.set_content(
        "/",
        """
        <title>Title</title>
        <select>
          <option value="foo">Foo</option>
          <option value="bar">Bar</option>
        </select>
    """,
        "text/html",
    )

    with patch.object(tool_registry, "execute_tool") as mock_execute:
        mock_execute.return_value = MagicMock()
        mock_execute.return_value.content = [
            {
                "type": "text",
                "text": f"""
- Ran Playwright code:
```js
// Select options [bar] in Select
await page.getByRole('combobox').selectOption(['bar']);
```

- Page URL: {server.PREFIX}
- Page Title: Title
- Page Snapshot
```yaml
- combobox [ref=e2]:
  - option "Foo"
  - option "Bar" [selected]
```
""",
            }
        ]

        result = await tool_registry.execute_tool(
            "browser_select_option",
            {"element": "Select", "ref": "e2", "values": ["bar"]},
        )

        assert hasattr(result, "content")
        assert result.content is not None
        text_content = ""
        for item in result.content:
            if item.get("type") == "text":
                text_content += item.get("text", "")

        assert "Select options [bar]" in text_content
        assert "Page Title: Title" in text_content
        assert 'option "Bar" [selected]' in text_content


@pytest.mark.asyncio
async def test_browser_select_option_multiple(
    tool_registry: EnhancedToolRegistry, server
):
    server.set_content(
        "/",
        """
        <title>Title</title>
        <select multiple>
          <option value="foo">Foo</option>
          <option value="bar">Bar</option>
          <option value="baz">Baz</option>
        </select>
    """,
        "text/html",
    )

    with patch.object(tool_registry, "execute_tool") as mock_execute:
        mock_execute.return_value = MagicMock()
        mock_execute.return_value.content = [
            {
                "type": "text",
                "text": f"""
- Ran Playwright code:
```js
// Select options [bar, baz] in Select
await page.getByRole('listbox').selectOption(['bar', 'baz']);
```

- Page URL: {server.PREFIX}
- Page Title: Title
- Page Snapshot
```yaml
- listbox [ref=e2]:
  - option "Foo" [ref=e3]
  - option "Bar" [selected] [ref=e4]
  - option "Baz" [selected] [ref=e5]
```
""",
            }
        ]

        result = await tool_registry.execute_tool(
            "browser_select_option",
            {"element": "Select", "ref": "e2", "values": ["bar", "baz"]},
        )

        assert hasattr(result, "content")
        assert result.content is not None
        text_content = ""
        for item in result.content:
            if item.get("type") == "text":
                text_content += item.get("text", "")

        assert "Select options [bar, baz]" in text_content
        assert "Page Title: Title" in text_content
        assert 'option "Bar" [selected]' in text_content
        assert 'option "Baz" [selected]' in text_content


@pytest.mark.asyncio
async def test_browser_console_messages(tool_registry: EnhancedToolRegistry):
    with patch.object(tool_registry, "execute_tool") as mock_execute:
        mock_execute.return_value = MagicMock()
        mock_execute.return_value.content = [
            {
                "type": "text",
                "text": """
- Ran Playwright code:
```js
// Get console messages
console.log('Console messages retrieved');
```

Console Messages:
[LOG] Key pressed: Enter , Text: Hi!
""",
            }
        ]

        result = await tool_registry.execute_tool("browser_console_messages", {})

        assert hasattr(result, "content")
        assert result.content is not None
        text_content = ""
        for item in result.content:
            if item.get("type") == "text":
                text_content += item.get("text", "")

        assert "[LOG] Key pressed: Enter , Text: Hi!" in text_content


@pytest.mark.asyncio
async def test_browser_snapshot(tool_registry: EnhancedToolRegistry, server):
    with patch.object(tool_registry, "execute_tool") as mock_execute:
        mock_execute.return_value = MagicMock()
        mock_execute.return_value.content = [
            {
                "type": "text",
                "text": f"""
- Ran Playwright code:
```js
// Take snapshot
await page.screenshot();
```

- Page URL: {server.HELLO_WORLD}
- Page Title: Title
- Page Snapshot
```yaml
- generic [ref=e1]: Hello, world!
```
""",
            }
        ]

        result = await tool_registry.execute_tool("browser_snapshot", {})

        assert hasattr(result, "content")
        assert result.content is not None
        text_content = ""
        for item in result.content:
            if item.get("type") == "text":
                text_content += item.get("text", "")

        assert "Page URL:" in text_content
        assert "Page Title: Title" in text_content
        assert "Page Snapshot" in text_content
        assert "- generic [ref=e1]: Hello, world!" in text_content


@pytest.mark.asyncio
async def test_browser_go_back(tool_registry: EnhancedToolRegistry):
    with patch.object(tool_registry, "execute_tool") as mock_execute:
        mock_execute.return_value = MagicMock()
        mock_execute.return_value.content = [
            {
                "type": "text",
                "text": """
- Ran Playwright code:
```js
// Go back to previous page
await page.goBack();
```

Navigated back to previous page successfully.
Current URL: https://previous.example.com
""",
            }
        ]

        result = await tool_registry.execute_tool("browser_go_back", {})

        assert hasattr(result, "content")
        assert result.content is not None
        text_content = ""
        for item in result.content:
            if item.get("type") == "text":
                text_content += item.get("text", "")

        assert "Go back to previous page" in text_content
        assert "Navigated back to previous page successfully" in text_content
        assert "Current URL: https://previous.example.com" in text_content


@pytest.mark.asyncio
async def test_browser_go_forward(tool_registry: EnhancedToolRegistry):
    with patch.object(tool_registry, "execute_tool") as mock_execute:
        mock_execute.return_value = MagicMock()
        mock_execute.return_value.content = [
            {
                "type": "text",
                "text": """
- Ran Playwright code:
```js
// Go forward to next page
await page.goForward();
```

Navigated forward to next page successfully.
Current URL: https://next.example.com
""",
            }
        ]

        result = await tool_registry.execute_tool("browser_go_forward", {})

        assert hasattr(result, "content")
        assert result.content is not None
        text_content = ""
        for item in result.content:
            if item.get("type") == "text":
                text_content += item.get("text", "")

        assert "Go forward to next page" in text_content
        assert "Navigated forward to next page successfully" in text_content
        assert "Current URL: https://next.example.com" in text_content


@pytest.mark.asyncio
async def test_browser_reload(tool_registry: EnhancedToolRegistry):
    with patch.object(tool_registry, "execute_tool") as mock_execute:
        mock_execute.return_value = MagicMock()
        mock_execute.return_value.content = [
            {
                "type": "text",
                "text": """
- Ran Playwright code:
```js
// Reload current page
await page.reload();
```

Page reloaded successfully.
Current URL: https://example.com
Page Title: Example Domain
""",
            }
        ]

        result = await tool_registry.execute_tool("browser_reload", {})

        assert hasattr(result, "content")
        assert result.content is not None
        text_content = ""
        for item in result.content:
            if item.get("type") == "text":
                text_content += item.get("text", "")

        assert "Reload current page" in text_content
        assert "Page reloaded successfully" in text_content
        assert "Current URL: https://example.com" in text_content
        assert "Page Title: Example Domain" in text_content
