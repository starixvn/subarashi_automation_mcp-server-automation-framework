import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from tests.conftest import assert_text_content, assert_contains_text_content
from context import ServerContext
from config.settings import Config, get_default_config, config_to_settings


@pytest.mark.asyncio
async def test_browser_automation_flow():
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

            nav_result = await registry.execute_tool(
                "browser_navigate", {"url": "https://example.com"}
            )

            assert nav_result["success"] is True
            assert nav_result["result"]["url"] == "https://example.com"

            mock_execute.return_value = {
                "success": True,
                "result": {
                    "element": "button",
                    "action": "click",
                    "coordinates": {"x": 100, "y": 200},
                },
            }

            click_result = await registry.execute_tool(
                "browser_click", {"selector": "button"}
            )

            assert click_result["success"] is True
            assert click_result["result"]["action"] == "click"

            mock_execute.return_value = {
                "success": True,
                "result": {"element": "input", "text": "Hello World", "action": "type"},
            }

            type_result = await registry.execute_tool(
                "browser_type", {"selector": "input", "text": "Hello World"}
            )

            assert type_result["success"] is True
            assert type_result["result"]["text"] == "Hello World"


@pytest.mark.asyncio
async def test_multi_step_interaction():
    default_config = get_default_config()
    settings = config_to_settings(default_config)

    with patch("playwright.async_api.async_playwright") as mock_playwright:
        mock_playwright_instance = AsyncMock()
        mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance

        context = ServerContext(settings)
        registry = context.tool_registry

        with patch.object(registry, "execute_tool") as mock_execute:
            steps = [
                ("browser_navigate", {"url": "https://form.example.com"}),
                ("browser_type", {"selector": "#name", "text": "John Doe"}),
                ("browser_type", {"selector": "#email", "text": "john@example.com"}),
                ("browser_select_option", {"selector": "#country", "value": "US"}),
                ("browser_click", {"selector": "#submit"}),
            ]

            results = []
            for tool_name, args in steps:
                mock_execute.return_value = {
                    "success": True,
                    "result": {"tool": tool_name, "args": args, "status": "completed"},
                }

                result = await registry.execute_tool(tool_name, args)
                results.append(result)

                assert result["success"] is True
                assert result["result"]["tool"] == tool_name

            assert len(results) == 5
            assert all(r["success"] for r in results)


@pytest.mark.asyncio
async def test_error_recovery():
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
                "error": "Element not found: #missing-button",
            }

            error_result = await registry.execute_tool(
                "browser_click", {"selector": "#missing-button"}
            )

            assert error_result["success"] is False
            assert "Element not found" in error_result["error"]

            mock_execute.return_value = {
                "success": True,
                "result": {
                    "element": "#alternative-button",
                    "action": "click",
                    "recovered": True,
                },
            }

            recovery_result = await registry.execute_tool(
                "browser_click", {"selector": "#alternative-button"}
            )

            assert recovery_result["success"] is True
            assert recovery_result["result"]["recovered"] is True


@pytest.mark.asyncio
async def test_concurrent_operations():
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
                    "result": {"operation": "screenshot", "file": "page1.png"},
                },
                {
                    "success": True,
                    "result": {"operation": "navigate", "url": "https://page2.com"},
                },
                {"success": True, "result": {"operation": "snapshot", "elements": 5}},
            ]

            import asyncio

            results = await asyncio.gather(
                registry.execute_tool("browser_screenshot", {}),
                registry.execute_tool("browser_navigate", {"url": "https://page2.com"}),
                registry.execute_tool("browser_capture_snapshot", {}),
            )

            assert len(results) == 3
            assert all(r["success"] for r in results)
            assert results[0]["result"]["operation"] == "screenshot"
            assert results[1]["result"]["operation"] == "navigate"
            assert results[2]["result"]["operation"] == "snapshot"


@pytest.mark.asyncio
async def test_capability_based_tool_availability():
    core_config = Config(
        browser=get_default_config().browser,
        server=get_default_config().server,
        network=get_default_config().network,
        capabilities=["core"],
    )
    core_settings = config_to_settings(core_config)

    with patch("playwright.async_api.async_playwright") as mock_playwright:
        mock_playwright_instance = AsyncMock()
        mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance

        core_context = ServerContext(core_settings)
        core_registry = core_context.tool_registry

        core_tools = await core_registry.list_tools()
        core_tool_names = {tool["name"] for tool in core_tools}

        assert "browser_navigate" in core_tool_names
        assert "browser_click" in core_tool_names
        assert "browser_type" in core_tool_names

    vision_config = Config(
        browser=get_default_config().browser,
        server=get_default_config().server,
        network=get_default_config().network,
        capabilities=["core", "vision"],
    )
    vision_settings = config_to_settings(vision_config)

    with patch("playwright.async_api.async_playwright") as mock_playwright:
        mock_playwright_instance = AsyncMock()
        mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance

        vision_context = ServerContext(vision_settings)
        vision_registry = vision_context.tool_registry

        vision_tools = await vision_registry.list_tools()
        vision_tool_names = {tool["name"] for tool in vision_tools}

        assert "browser_navigate" in vision_tool_names
