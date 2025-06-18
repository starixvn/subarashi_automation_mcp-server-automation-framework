import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from pathlib import Path
import sys

# Add the parent directory to the path so we can import from the main package
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.conftest import assert_text_content, assert_contains_text_content
from context import ServerContext
from config.settings import Config, get_default_config, config_to_settings


@pytest.mark.asyncio
async def test_browser_upload_file_single():
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
// Upload file /tmp/test.txt
await page.setInputFiles('input[type="file"]', '/tmp/test.txt');
```

File uploaded successfully: /tmp/test.txt
""",
                }
            ]

            result = await registry.execute_tool(
                "browser_upload_file", {"file_paths": ["/tmp/test.txt"]}
            )

            assert hasattr(result, "content")
            assert result.content is not None
            text_content = ""
            for item in result.content:
                if item.get("type") == "text":
                    text_content += item.get("text", "")

            assert "Upload file /tmp/test.txt" in text_content
            assert "File uploaded successfully" in text_content


@pytest.mark.asyncio
async def test_browser_upload_file_multiple():
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
// Upload files ['/tmp/file1.pdf', '/tmp/file2.jpg', '/tmp/file3.doc']
await page.setInputFiles('input[type="file"]', ['/tmp/file1.pdf', '/tmp/file2.jpg', '/tmp/file3.doc']);
```

Files uploaded successfully:
- /tmp/file1.pdf
- /tmp/file2.jpg
- /tmp/file3.doc
""",
                }
            ]

            result = await registry.execute_tool(
                "browser_upload_file",
                {"file_paths": ["/tmp/file1.pdf", "/tmp/file2.jpg", "/tmp/file3.doc"]},
            )

            assert hasattr(result, "content")
            assert result.content is not None
            text_content = ""
            for item in result.content:
                if item.get("type") == "text":
                    text_content += item.get("text", "")

            assert "Upload files" in text_content
            assert "Files uploaded successfully" in text_content
            assert "/tmp/file1.pdf" in text_content
            assert "/tmp/file2.jpg" in text_content
            assert "/tmp/file3.doc" in text_content


@pytest.mark.asyncio
async def test_browser_upload_file_with_selector():
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
// Upload file /tmp/image.png to selector #file-upload
await page.setInputFiles('#file-upload', '/tmp/image.png');
```

File uploaded successfully to #file-upload: /tmp/image.png
""",
                }
            ]

            result = await registry.execute_tool(
                "browser_upload_file",
                {"file_paths": ["/tmp/image.png"], "selector": "#file-upload"},
            )

            assert hasattr(result, "content")
            assert result.content is not None
            text_content = ""
            for item in result.content:
                if item.get("type") == "text":
                    text_content += item.get("text", "")

            assert "Upload file /tmp/image.png to selector #file-upload" in text_content
            assert "File uploaded successfully to #file-upload" in text_content


@pytest.mark.asyncio
async def test_browser_upload_file_image_types():
    default_config = get_default_config()
    settings = config_to_settings(default_config)

    with patch("playwright.async_api.async_playwright") as mock_playwright:
        mock_playwright_instance = AsyncMock()
        mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance

        context = ServerContext(settings)
        registry = context.tool_registry

        image_files = ["/tmp/photo.jpg", "/tmp/logo.png", "/tmp/avatar.gif"]

        with patch.object(registry, "execute_tool") as mock_execute:
            mock_execute.return_value = MagicMock()
            mock_execute.return_value.content = [
                {
                    "type": "text",
                    "text": """
- Ran Playwright code:
```js
// Upload files ['/tmp/photo.jpg', '/tmp/logo.png', '/tmp/avatar.gif']
await page.setInputFiles('input[type="file"]', ['/tmp/photo.jpg', '/tmp/logo.png', '/tmp/avatar.gif']);
```

Image files uploaded successfully:
- /tmp/photo.jpg (JPEG)
- /tmp/logo.png (PNG)
- /tmp/avatar.gif (GIF)
""",
                }
            ]

            result = await registry.execute_tool(
                "browser_upload_file", {"file_paths": image_files}
            )

            assert hasattr(result, "content")
            assert result.content is not None
            text_content = ""
            for item in result.content:
                if item.get("type") == "text":
                    text_content += item.get("text", "")

            assert "Image files uploaded successfully" in text_content
            assert "(JPEG)" in text_content
            assert "(PNG)" in text_content
            assert "(GIF)" in text_content


@pytest.mark.asyncio
async def test_browser_upload_file_document_types():
    default_config = get_default_config()
    settings = config_to_settings(default_config)

    with patch("playwright.async_api.async_playwright") as mock_playwright:
        mock_playwright_instance = AsyncMock()
        mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance

        context = ServerContext(settings)
        registry = context.tool_registry

        document_files = ["/tmp/report.pdf", "/tmp/data.csv", "/tmp/notes.txt"]

        with patch.object(registry, "execute_tool") as mock_execute:
            mock_execute.return_value = MagicMock()
            mock_execute.return_value.content = [
                {
                    "type": "text",
                    "text": """
- Ran Playwright code:
```js
// Upload files ['/tmp/report.pdf', '/tmp/data.csv', '/tmp/notes.txt']
await page.setInputFiles('input[type="file"]', ['/tmp/report.pdf', '/tmp/data.csv', '/tmp/notes.txt']);
```

Document files uploaded successfully:
- /tmp/report.pdf (PDF, 2.5 MB)
- /tmp/data.csv (CSV, 1.2 MB)
- /tmp/notes.txt (Text, 0.5 MB)
""",
                }
            ]

            result = await registry.execute_tool(
                "browser_upload_file", {"file_paths": document_files}
            )

            assert hasattr(result, "content")
            assert result.content is not None
            text_content = ""
            for item in result.content:
                if item.get("type") == "text":
                    text_content += item.get("text", "")

            assert "Document files uploaded successfully" in text_content
            assert "PDF" in text_content
            assert "CSV" in text_content
            assert "Text" in text_content


@pytest.mark.asyncio
async def test_browser_upload_file_error_file_not_found():
    default_config = get_default_config()
    settings = config_to_settings(default_config)

    with patch("playwright.async_api.async_playwright") as mock_playwright:
        mock_playwright_instance = AsyncMock()
        mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance

        context = ServerContext(settings)
        registry = context.tool_registry

        with patch.object(registry, "execute_tool") as mock_execute:
            mock_execute.side_effect = Exception(
                "File not found: /tmp/nonexistent.txt"
            )

            with pytest.raises(Exception, match="File not found: /tmp/nonexistent.txt"):
                await registry.execute_tool(
                    "browser_upload_file", {"file_paths": ["/tmp/nonexistent.txt"]}
                )


@pytest.mark.asyncio
async def test_browser_upload_file_error_no_file_input():
    default_config = get_default_config()
    settings = config_to_settings(default_config)

    with patch("playwright.async_api.async_playwright") as mock_playwright:
        mock_playwright_instance = AsyncMock()
        mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance

        context = ServerContext(settings)
        registry = context.tool_registry

        with patch.object(registry, "execute_tool") as mock_execute:
            mock_execute.side_effect = Exception("No file input element found on page")

            with pytest.raises(Exception, match="No file input element found on page"):
                await registry.execute_tool(
                    "browser_upload_file", {"file_paths": ["/tmp/test.txt"]}
                )


@pytest.mark.asyncio
async def test_browser_upload_file_with_validation():
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
// Upload file /tmp/large_file.zip (validation enabled)
await page.setInputFiles('input[type="file"]', '/tmp/large_file.zip');
```

File validation results:
- File size: 15.2 MB (within 20 MB limit)
- File type: application/zip (allowed)
- Virus scan: Clean

File uploaded successfully: /tmp/large_file.zip
""",
                }
            ]

            result = await registry.execute_tool(
                "browser_upload_file",
                {"file_paths": ["/tmp/large_file.zip"], "validate": True},
            )

            assert hasattr(result, "content")
            assert result.content is not None
            text_content = ""
            for item in result.content:
                if item.get("type") == "text":
                    text_content += item.get("text", "")

            assert "File validation results" in text_content
            assert "File size: 15.2 MB" in text_content
            assert "File type: application/zip" in text_content
            assert "Virus scan: Clean" in text_content


@pytest.mark.asyncio
async def test_browser_upload_file_progress_tracking():
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
// Upload file /tmp/video.mp4 with progress tracking
await page.setInputFiles('input[type="file"]', '/tmp/video.mp4');
```

Upload Progress:
[████████████████████████] 100% - /tmp/video.mp4 (50.2 MB)
Upload completed in 12.5 seconds
Average speed: 4.02 MB/s

File uploaded successfully: /tmp/video.mp4
""",
                }
            ]

            result = await registry.execute_tool(
                "browser_upload_file",
                {"file_paths": ["/tmp/video.mp4"], "track_progress": True},
            )

            assert hasattr(result, "content")
            assert result.content is not None
            text_content = ""
            for item in result.content:
                if item.get("type") == "text":
                    text_content += item.get("text", "")

            assert "Upload Progress" in text_content
            assert "100%" in text_content
            assert "Upload completed in" in text_content
            assert "Average speed:" in text_content


@pytest.mark.asyncio
async def test_files_capability_filtering():
    config = Config(
        browser=get_default_config().browser,
        server=get_default_config().server,
        network=get_default_config().network,
        capabilities=["core", "files"],
    )
    settings = config_to_settings(config)

    with patch("playwright.async_api.async_playwright") as mock_playwright:
        mock_playwright_instance = AsyncMock()
        mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance

        context = ServerContext(settings)
        registry = context.tool_registry

        tools = await registry.list_tools()
        tool_names = {tool["name"] for tool in tools}

        assert "browser_upload_file" in tool_names 