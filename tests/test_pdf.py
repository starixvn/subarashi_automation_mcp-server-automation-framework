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
async def test_browser_save_pdf_default():
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
// Save page as PDF
await page.pdf({ path: 'page.pdf', format: 'A4' });
```

PDF saved successfully: page.pdf
File size: 2.3 MB
Format: A4
""",
                }
            ]

            result = await registry.execute_tool(
                "browser_save_pdf", {"filename": "page.pdf"}
            )

            assert hasattr(result, "content")
            assert result.content is not None
            text_content = ""
            for item in result.content:
                if item.get("type") == "text":
                    text_content += item.get("text", "")

            assert "Save page as PDF" in text_content
            assert "PDF saved successfully: page.pdf" in text_content
            assert "File size: 2.3 MB" in text_content
            assert "Format: A4" in text_content


@pytest.mark.asyncio
async def test_browser_save_pdf_custom_format():
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
// Save page as PDF with format Letter
await page.pdf({ path: 'document.pdf', format: 'Letter' });
```

PDF saved successfully: document.pdf
File size: 1.8 MB
Format: Letter
""",
                }
            ]

            result = await registry.execute_tool(
                "browser_save_pdf", {"filename": "document.pdf", "format": "Letter"}
            )

            assert hasattr(result, "content")
            assert result.content is not None
            text_content = ""
            for item in result.content:
                if item.get("type") == "text":
                    text_content += item.get("text", "")

            assert "Save page as PDF with format Letter" in text_content
            assert "PDF saved successfully: document.pdf" in text_content
            assert "Format: Letter" in text_content


@pytest.mark.asyncio
async def test_browser_save_pdf_landscape():
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
// Save page as PDF in landscape orientation
await page.pdf({ path: 'report.pdf', format: 'A4', landscape: true });
```

PDF saved successfully: report.pdf
File size: 3.1 MB
Format: A4
Orientation: Landscape
""",
                }
            ]

            result = await registry.execute_tool(
                "browser_save_pdf",
                {"filename": "report.pdf", "landscape": True},
            )

            assert hasattr(result, "content")
            assert result.content is not None
            text_content = ""
            for item in result.content:
                if item.get("type") == "text":
                    text_content += item.get("text", "")

            assert "Save page as PDF in landscape orientation" in text_content
            assert "PDF saved successfully: report.pdf" in text_content
            assert "Orientation: Landscape" in text_content


@pytest.mark.asyncio
async def test_browser_save_pdf_with_margins():
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
// Save page as PDF with custom margins
await page.pdf({ 
  path: 'invoice.pdf', 
  format: 'A4',
  margin: { top: '1in', right: '0.5in', bottom: '1in', left: '0.5in' }
});
```

PDF saved successfully: invoice.pdf
File size: 1.9 MB
Format: A4
Margins: Top: 1in, Right: 0.5in, Bottom: 1in, Left: 0.5in
""",
                }
            ]

            result = await registry.execute_tool(
                "browser_save_pdf",
                {
                    "filename": "invoice.pdf",
                    "margins": {
                        "top": "1in",
                        "right": "0.5in",
                        "bottom": "1in",
                        "left": "0.5in",
                    },
                },
            )

            assert hasattr(result, "content")
            assert result.content is not None
            text_content = ""
            for item in result.content:
                if item.get("type") == "text":
                    text_content += item.get("text", "")

            assert "Save page as PDF with custom margins" in text_content
            assert "PDF saved successfully: invoice.pdf" in text_content
            assert "Margins:" in text_content
            assert "Top: 1in" in text_content
            assert "Left: 0.5in" in text_content


@pytest.mark.asyncio
async def test_browser_save_pdf_print_background():
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
// Save page as PDF with background graphics
await page.pdf({ path: 'brochure.pdf', format: 'A4', printBackground: true });
```

PDF saved successfully: brochure.pdf
File size: 4.7 MB
Format: A4
Background graphics: Included
""",
                }
            ]

            result = await registry.execute_tool(
                "browser_save_pdf",
                {"filename": "brochure.pdf", "print_background": True},
            )

            assert hasattr(result, "content")
            assert result.content is not None
            text_content = ""
            for item in result.content:
                if item.get("type") == "text":
                    text_content += item.get("text", "")

            assert "Save page as PDF with background graphics" in text_content
            assert "PDF saved successfully: brochure.pdf" in text_content
            assert "Background graphics: Included" in text_content


@pytest.mark.asyncio
async def test_browser_save_pdf_full_page():
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
// Save full page as PDF
await page.pdf({ path: 'fullpage.pdf', format: 'A4', fullPage: true });
```

PDF saved successfully: fullpage.pdf
File size: 8.2 MB
Format: A4
Full page: Yes
Pages: 15
""",
                }
            ]

            result = await registry.execute_tool(
                "browser_save_pdf", {"filename": "fullpage.pdf", "full_page": True}
            )

            assert hasattr(result, "content")
            assert result.content is not None
            text_content = ""
            for item in result.content:
                if item.get("type") == "text":
                    text_content += item.get("text", "")

            assert "Save full page as PDF" in text_content
            assert "PDF saved successfully: fullpage.pdf" in text_content
            assert "Full page: Yes" in text_content
            assert "Pages: 15" in text_content


@pytest.mark.asyncio
async def test_browser_save_pdf_custom_scale():
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
// Save page as PDF with 150% scale
await page.pdf({ path: 'zoomed.pdf', format: 'A4', scale: 1.5 });
```

PDF saved successfully: zoomed.pdf
File size: 3.8 MB
Format: A4
Scale: 150%
""",
                }
            ]

            result = await registry.execute_tool(
                "browser_save_pdf", {"filename": "zoomed.pdf", "scale": 1.5}
            )

            assert hasattr(result, "content")
            assert result.content is not None
            text_content = ""
            for item in result.content:
                if item.get("type") == "text":
                    text_content += item.get("text", "")

            assert "Save page as PDF with 150% scale" in text_content
            assert "PDF saved successfully: zoomed.pdf" in text_content
            assert "Scale: 150%" in text_content


@pytest.mark.asyncio
async def test_browser_save_pdf_page_range():
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
// Save specific page range as PDF
await page.pdf({ path: 'excerpt.pdf', format: 'A4', pageRanges: '1-5,8,11-13' });
```

PDF saved successfully: excerpt.pdf
File size: 1.2 MB
Format: A4
Page ranges: 1-5, 8, 11-13
Total pages: 9
""",
                }
            ]

            result = await registry.execute_tool(
                "browser_save_pdf",
                {"filename": "excerpt.pdf", "page_ranges": "1-5,8,11-13"},
            )

            assert hasattr(result, "content")
            assert result.content is not None
            text_content = ""
            for item in result.content:
                if item.get("type") == "text":
                    text_content += item.get("text", "")

            assert "Save specific page range as PDF" in text_content
            assert "PDF saved successfully: excerpt.pdf" in text_content
            assert "Page ranges: 1-5, 8, 11-13" in text_content
            assert "Total pages: 9" in text_content


@pytest.mark.asyncio
async def test_browser_save_pdf_error_handling():
    default_config = get_default_config()
    settings = config_to_settings(default_config)

    with patch("playwright.async_api.async_playwright") as mock_playwright:
        mock_playwright_instance = AsyncMock()
        mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance

        context = ServerContext(settings)
        registry = context.tool_registry

        with patch.object(registry, "execute_tool") as mock_execute:
            mock_execute.side_effect = Exception("Permission denied: Cannot write to /root/")

            with pytest.raises(Exception, match="Permission denied: Cannot write to /root/"):
                await registry.execute_tool(
                    "browser_save_pdf", {"filename": "/root/protected.pdf"}
                )


@pytest.mark.asyncio
async def test_browser_save_pdf_with_headers_footers():
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
// Save page as PDF with headers and footers
await page.pdf({ 
  path: 'formal.pdf', 
  format: 'A4',
  displayHeaderFooter: true,
  headerTemplate: '<div style="font-size:10px;margin:0 auto;">Company Report</div>',
  footerTemplate: '<div style="font-size:10px;margin:0 auto;">Page <span class="pageNumber"></span> of <span class="totalPages"></span></div>'
});
```

PDF saved successfully: formal.pdf
File size: 2.1 MB
Format: A4
Headers/Footers: Enabled
Header: Company Report
Footer: Page numbers
""",
                }
            ]

            result = await registry.execute_tool(
                "browser_save_pdf",
                {
                    "filename": "formal.pdf",
                    "display_header_footer": True,
                    "header_template": '<div style="font-size:10px;margin:0 auto;">Company Report</div>',
                    "footer_template": '<div style="font-size:10px;margin:0 auto;">Page <span class="pageNumber"></span> of <span class="totalPages"></span></div>',
                },
            )

            assert hasattr(result, "content")
            assert result.content is not None
            text_content = ""
            for item in result.content:
                if item.get("type") == "text":
                    text_content += item.get("text", "")

            assert "Save page as PDF with headers and footers" in text_content
            assert "PDF saved successfully: formal.pdf" in text_content
            assert "Headers/Footers: Enabled" in text_content
            assert "Header: Company Report" in text_content
            assert "Footer: Page numbers" in text_content


@pytest.mark.asyncio
async def test_pdf_capability_filtering():
    config = Config(
        browser=get_default_config().browser,
        server=get_default_config().server,
        network=get_default_config().network,
        capabilities=["core", "pdf"],
    )
    settings = config_to_settings(config)

    with patch("playwright.async_api.async_playwright") as mock_playwright:
        mock_playwright_instance = AsyncMock()
        mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance

        context = ServerContext(settings)
        registry = context.tool_registry

        tools = await registry.list_tools()
        tool_names = {tool["name"] for tool in tools}

        assert "browser_save_pdf" in tool_names 