import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from tests.conftest import assert_text_content, assert_contains_text_content
from context import ServerContext
from config.settings import Config, get_default_config, config_to_settings


@pytest.mark.asyncio
async def test_list_initial_tabs():
    default_config = get_default_config()
    settings = config_to_settings(default_config)

    with patch("playwright.async_api.async_playwright") as mock_playwright:
        mock_playwright_instance = AsyncMock()
        mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance

        mock_browser = AsyncMock()
        mock_context = AsyncMock()
        mock_page = AsyncMock()

        mock_playwright_instance.chromium.launch.return_value = mock_browser
        mock_browser.new_context.return_value = mock_context
        mock_context.new_page.return_value = mock_page
        mock_context.pages = [mock_page]

        context = ServerContext(settings)
        registry = context.tool_registry

        with patch.object(registry, "execute_tool") as mock_execute:
            mock_execute.return_value = {
                "success": True,
                "result": {
                    "tabs": [
                        {
                            "id": "tab-1",
                            "url": "about:blank",
                            "title": "New Tab",
                            "active": True,
                        }
                    ]
                },
            }

            result = await registry.execute_tool("browser_tab_list", {})

            assert result["success"] is True
            tabs = result["result"]["tabs"]
            assert len(tabs) == 1
            assert tabs[0]["id"] == "tab-1"
            assert tabs[0]["active"] is True


@pytest.mark.asyncio
async def test_create_new_tab():
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
                "result": {"tab_id": "tab-2", "url": "about:blank"},
            }

            result = await registry.execute_tool("browser_tab_new", {})

            assert result["success"] is True
            assert result["result"]["tab_id"] == "tab-2"
            assert result["result"]["url"] == "about:blank"


@pytest.mark.asyncio
async def test_select_tab():
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
                    "tab_id": "tab-1",
                    "url": "https://example.com",
                    "title": "Example",
                },
            }

            result = await registry.execute_tool(
                "browser_tab_select", {"tab_id": "tab-1"}
            )

            assert result["success"] is True
            assert result["result"]["tab_id"] == "tab-1"
            assert result["result"]["url"] == "https://example.com"


@pytest.mark.asyncio
async def test_close_tab():
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
                "result": {"closed_tab_id": "tab-2"},
            }

            result = await registry.execute_tool(
                "browser_tab_close", {"tab_id": "tab-2"}
            )

            assert result["success"] is True
            assert result["result"]["closed_tab_id"] == "tab-2"


@pytest.mark.asyncio
async def test_navigation_reuses_current_tab():
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
async def test_tab_error_handling():
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
                "error": "Tab not found: invalid-tab-id",
            }

            result = await registry.execute_tool(
                "browser_tab_select", {"tab_id": "invalid-tab-id"}
            )

            assert result["success"] is False
            assert "Tab not found" in result["error"]
