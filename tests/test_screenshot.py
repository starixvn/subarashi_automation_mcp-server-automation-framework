import pytest
import tempfile
import base64
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock

from tests.conftest import assert_text_content, assert_contains_text_content
from context import ServerContext
from config.settings import Config, get_default_config, config_to_settings


@pytest.mark.asyncio
async def test_screenshot_viewport():
    default_config = get_default_config()
    settings = config_to_settings(default_config)

    with patch("playwright.async_api.async_playwright") as mock_playwright:
        mock_playwright_instance = AsyncMock()
        mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance

        context = ServerContext(settings)
        registry = context.tool_registry

        with patch.object(registry, "execute_tool") as mock_execute:
            mock_image_data = base64.b64encode(b"fake_image_data").decode()
            mock_execute.return_value = {
                "success": True,
                "result": {
                    "screenshot": mock_image_data,
                    "format": "png",
                    "width": 1280,
                    "height": 720,
                },
            }

            result = await registry.execute_tool("browser_screenshot", {})

            assert result["success"] is True
            assert "screenshot" in result["result"]
            assert result["result"]["format"] == "png"
            assert result["result"]["width"] == 1280
            assert result["result"]["height"] == 720


@pytest.mark.asyncio
async def test_screenshot_element():
    default_config = get_default_config()
    settings = config_to_settings(default_config)

    with patch("playwright.async_api.async_playwright") as mock_playwright:
        mock_playwright_instance = AsyncMock()
        mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance

        context = ServerContext(settings)
        registry = context.tool_registry

        with patch.object(registry, "execute_tool") as mock_execute:
            mock_image_data = base64.b64encode(b"fake_element_image").decode()
            mock_execute.return_value = {
                "success": True,
                "result": {
                    "screenshot": mock_image_data,
                    "format": "png",
                    "element": "button",
                    "width": 100,
                    "height": 40,
                },
            }

            result = await registry.execute_tool(
                "browser_screenshot", {"selector": "button"}
            )

            assert result["success"] is True
            assert "screenshot" in result["result"]
            assert result["result"]["element"] == "button"


@pytest.mark.asyncio
async def test_screenshot_custom_filename():
    default_config = get_default_config()
    settings = config_to_settings(default_config)

    with patch("playwright.async_api.async_playwright") as mock_playwright:
        mock_playwright_instance = AsyncMock()
        mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance

        context = ServerContext(settings)
        registry = context.tool_registry

        with patch.object(registry, "execute_tool") as mock_execute:
            mock_execute.return_value = {
                "success": True,
                "result": {
                    "filename": "custom_screenshot.png",
                    "path": "/tmp/custom_screenshot.png",
                    "format": "png",
                },
            }

            result = await registry.execute_tool(
                "browser_screenshot", {"filename": "custom_screenshot.png"}
            )

            assert result["success"] is True
            assert result["result"]["filename"] == "custom_screenshot.png"
            assert "path" in result["result"]


@pytest.mark.asyncio
async def test_screenshot_raw_format():
    default_config = get_default_config()
    settings = config_to_settings(default_config)

    with patch("playwright.async_api.async_playwright") as mock_playwright:
        mock_playwright_instance = AsyncMock()
        mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance

        context = ServerContext(settings)
        registry = context.tool_registry

        with patch.object(registry, "execute_tool") as mock_execute:
            mock_execute.return_value = {
                "success": True,
                "result": {
                    "raw_data": b"fake_raw_image_data",
                    "format": "png",
                    "encoding": "raw",
                },
            }

            result = await registry.execute_tool(
                "browser_screenshot", {"format": "raw"}
            )

            assert result["success"] is True
            assert "raw_data" in result["result"]
            assert result["result"]["encoding"] == "raw"


@pytest.mark.asyncio
async def test_screenshot_output_directory():
    default_config = get_default_config()
    settings = config_to_settings(default_config)

    with tempfile.TemporaryDirectory() as temp_dir:
        with patch("playwright.async_api.async_playwright") as mock_playwright:
            mock_playwright_instance = AsyncMock()
            mock_playwright.return_value.__aenter__.return_value = (
                mock_playwright_instance
            )

            context = ServerContext(settings)
            registry = context.tool_registry

            with patch.object(registry, "execute_tool") as mock_execute:
                expected_path = str(Path(temp_dir) / "screenshot.png")
                mock_execute.return_value = {
                    "success": True,
                    "result": {
                        "filename": "screenshot.png",
                        "path": expected_path,
                        "directory": temp_dir,
                    },
                }

                result = await registry.execute_tool(
                    "browser_screenshot", {"output_dir": temp_dir}
                )

                assert result["success"] is True
                assert result["result"]["directory"] == temp_dir
                assert temp_dir in result["result"]["path"]


@pytest.mark.asyncio
async def test_screenshot_image_responses_omit():
    config = Config(
        browser=get_default_config().browser,
        server=get_default_config().server,
        network=get_default_config().network,
        capabilities=["core"],
    )
    settings = config_to_settings(config)

    with patch("playwright.async_api.async_playwright") as mock_playwright:
        mock_playwright_instance = AsyncMock()
        mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance

        context = ServerContext(settings)
        registry = context.tool_registry

        with patch.object(registry, "execute_tool") as mock_execute:
            mock_execute.return_value = {
                "success": True,
                "result": {
                    "filename": "screenshot.png",
                    "path": "/tmp/screenshot.png",
                    "message": "Screenshot saved (image data omitted)",
                },
            }

            result = await registry.execute_tool(
                "browser_screenshot", {"omit_image": True}
            )

            assert result["success"] is True
            assert "Screenshot saved" in result["result"]["message"]
            assert "screenshot" not in result["result"]  # Image data omitted


@pytest.mark.asyncio
async def test_screenshot_error_handling():
    default_config = get_default_config()
    settings = config_to_settings(default_config)

    with patch("playwright.async_api.async_playwright") as mock_playwright:
        mock_playwright_instance = AsyncMock()
        mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance

        context = ServerContext(settings)
        registry = context.tool_registry

        with patch.object(registry, "execute_tool") as mock_execute:
            mock_execute.return_value = {
                "success": False,
                "error": "Element not found: invalid-selector",
            }

            result = await registry.execute_tool(
                "browser_screenshot", {"selector": "invalid-selector"}
            )

            assert result["success"] is False
            assert "Element not found" in result["error"]


@pytest.mark.asyncio
async def test_screenshot_base64_encoding():
    default_config = get_default_config()
    settings = config_to_settings(default_config)

    with patch("playwright.async_api.async_playwright") as mock_playwright:
        mock_playwright_instance = AsyncMock()
        mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance

        context = ServerContext(settings)
        registry = context.tool_registry

        with patch.object(registry, "execute_tool") as mock_execute:
            original_data = b"fake_image_data_for_testing"
            encoded_data = base64.b64encode(original_data).decode()

            mock_execute.return_value = {
                "success": True,
                "result": {
                    "screenshot": encoded_data,
                    "format": "png",
                    "encoding": "base64",
                },
            }

            result = await registry.execute_tool(
                "browser_screenshot", {"encoding": "base64"}
            )

            assert result["success"] is True
            assert result["result"]["encoding"] == "base64"

            decoded_data = base64.b64decode(result["result"]["screenshot"])
            assert decoded_data == original_data
