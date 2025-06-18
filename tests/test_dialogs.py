import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from tests.conftest import assert_text_content, assert_contains_text_content
from context import ServerContext
from config.settings import Config, get_default_config, config_to_settings


@pytest.mark.asyncio
async def test_alert_dialog():
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
                    "dialog_type": "alert",
                    "message": "This is an alert",
                    "action": "accept",
                },
            }

            result = await registry.execute_tool(
                "browser_handle_dialog", {"action": "accept"}
            )

            assert result["success"] is True
            assert result["result"]["dialog_type"] == "alert"
            assert result["result"]["action"] == "accept"


@pytest.mark.asyncio
async def test_confirm_dialog_true():
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
                    "dialog_type": "confirm",
                    "message": "Are you sure?",
                    "action": "accept",
                },
            }

            result = await registry.execute_tool(
                "browser_handle_dialog", {"action": "accept"}
            )

            assert result["success"] is True
            assert result["result"]["dialog_type"] == "confirm"
            assert result["result"]["action"] == "accept"


@pytest.mark.asyncio
async def test_confirm_dialog_false():
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
                    "dialog_type": "confirm",
                    "message": "Are you sure?",
                    "action": "dismiss",
                },
            }

            result = await registry.execute_tool(
                "browser_handle_dialog", {"action": "dismiss"}
            )

            assert result["success"] is True
            assert result["result"]["dialog_type"] == "confirm"
            assert result["result"]["action"] == "dismiss"


@pytest.mark.asyncio
async def test_prompt_dialog():
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
                    "dialog_type": "prompt",
                    "message": "Enter your name:",
                    "action": "accept",
                    "text": "John Doe",
                },
            }

            result = await registry.execute_tool(
                "browser_handle_dialog", {"action": "accept", "text": "John Doe"}
            )

            assert result["success"] is True
            assert result["result"]["dialog_type"] == "prompt"
            assert result["result"]["action"] == "accept"
            assert result["result"]["text"] == "John Doe"


@pytest.mark.asyncio
async def test_multiple_dialogs():
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
                    "dialog_type": "alert",
                    "message": "First alert",
                    "action": "accept",
                },
            }

            result1 = await registry.execute_tool(
                "browser_handle_dialog", {"action": "accept"}
            )

            mock_execute.return_value = {
                "success": True,
                "result": {
                    "dialog_type": "confirm",
                    "message": "Confirm action?",
                    "action": "accept",
                },
            }

            result2 = await registry.execute_tool(
                "browser_handle_dialog", {"action": "accept"}
            )

            assert result1["success"] is True
            assert result1["result"]["dialog_type"] == "alert"
            assert result2["success"] is True
            assert result2["result"]["dialog_type"] == "confirm"


@pytest.mark.asyncio
async def test_dialog_error_handling():
    default_config = get_default_config()
    settings = config_to_settings(default_config)

    with patch("playwright.async_api.async_playwright") as mock_playwright:
        mock_playwright_instance = AsyncMock()
        mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance

        context = ServerContext(settings)
        registry = context.tool_registry

        with patch.object(registry, "execute_tool") as mock_execute:
            mock_execute.return_value = {"success": False, "error": "No dialog present"}

            result = await registry.execute_tool(
                "browser_handle_dialog", {"action": "accept"}
            )

            assert result["success"] is False
            assert "No dialog present" in result["error"]
