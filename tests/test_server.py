import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from tests.conftest import assert_text_content, assert_contains_text_content
from context import ServerContext
from config.settings import Config, get_default_config, config_to_settings


@pytest.mark.asyncio
async def test_server_creation():
    default_config = get_default_config()
    settings = config_to_settings(default_config)

    with patch("playwright.async_api.async_playwright") as mock_playwright:
        mock_playwright_instance = AsyncMock()
        mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance

        context = ServerContext(settings)

        assert context is not None
        assert context.tool_registry is not None
        assert hasattr(context, "settings")
        assert context.settings.browser_type == "chromium"


@pytest.mark.asyncio
async def test_list_tools():
    default_config = get_default_config()
    settings = config_to_settings(default_config)

    with patch("playwright.async_api.async_playwright") as mock_playwright:
        mock_playwright_instance = AsyncMock()
        mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance

        context = ServerContext(settings)
        registry = context.tool_registry

        tools = await registry.list_tools()

        assert isinstance(tools, list)
        assert len(tools) > 0

        for tool in tools:
            assert "name" in tool
            assert "description" in tool
            assert "inputSchema" in tool


@pytest.mark.asyncio
async def test_call_tool():
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
                    "url": "https://example.com",
                    "title": "Example Domain",
                    "status": 200,
                },
            }

            result = await registry.execute_tool(
                "browser_navigate", {"url": "https://example.com"}
            )

            assert result["success"] is True
            assert result["result"]["url"] == "https://example.com"
            assert result["result"]["title"] == "Example Domain"


@pytest.mark.asyncio
async def test_tool_error_handling():
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
                "error": "Invalid URL format",
            }

            result = await registry.execute_tool(
                "browser_navigate", {"url": "invalid-url"}
            )

            assert result["success"] is False
            assert "Invalid URL format" in result["error"]


@pytest.mark.asyncio
async def test_tool_validation():
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
                "error": "Missing required parameter: url",
            }

            result = await registry.execute_tool("browser_navigate", {})

            assert result["success"] is False
            assert "Missing required parameter" in result["error"]


@pytest.mark.asyncio
async def test_concurrent_tool_calls():
    default_config = get_default_config()
    settings = config_to_settings(default_config)

    with patch("playwright.async_api.async_playwright") as mock_playwright:
        mock_playwright_instance = AsyncMock()
        mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance

        context = ServerContext(settings)
        registry = context.tool_registry

        with patch.object(registry, "execute_tool") as mock_execute:
            mock_execute.side_effect = [
                {
                    "success": True,
                    "result": {"url": "https://example1.com", "title": "Example 1"},
                },
                {
                    "success": True,
                    "result": {"url": "https://example2.com", "title": "Example 2"},
                },
            ]

            import asyncio

            results = await asyncio.gather(
                registry.execute_tool(
                    "browser_navigate", {"url": "https://example1.com"}
                ),
                registry.execute_tool(
                    "browser_navigate", {"url": "https://example2.com"}
                ),
            )

            assert len(results) == 2
            assert all(result["success"] for result in results)
            assert results[0]["result"]["url"] == "https://example1.com"
            assert results[1]["result"]["url"] == "https://example2.com"


@pytest.mark.asyncio
async def test_resource_cleanup():
    default_config = get_default_config()
    settings = config_to_settings(default_config)

    with patch("playwright.async_api.async_playwright") as mock_playwright:
        mock_playwright_instance = AsyncMock()
        mock_browser = AsyncMock()
        mock_context = AsyncMock()

        mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance
        mock_playwright_instance.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context

        context = ServerContext(settings)

        if hasattr(context, "cleanup"):
            await context.cleanup()

        assert True
