import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import sys
from pathlib import Path

# Add the parent directory to the path so we can import from the main package
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.conftest import assert_text_content, assert_contains_text_content
from context import ServerContext
from config.settings import Config, get_default_config, config_to_settings
from tools.core import get_core_tools
from services.core_service import CoreService
from services.base_service import ServiceResult


@pytest.mark.asyncio
async def test_browser_navigate():
    # Test navigation functionality
    core_tools = get_core_tools(capture_snapshot=False)
    navigate_tool = next(
        tool for tool in core_tools if tool.schema.name == "browser_navigate"
    )

    # Mock service result
    mock_service_result = {
        "success": True,
        "data": {"url": "https://example.com"},
        "message": "Navigated to https://example.com",
    }

    # Create mock context
    mock_context = MagicMock()

    with patch.object(CoreService, "navigate_to_url", return_value=mock_service_result):
        result = await navigate_tool.handle(
            mock_context, {"url": "https://example.com"}
        )

        # Test ToolResult structure
        assert result.code == ["# Navigate to https://example.com"]
        assert result.capture_snapshot is False
        assert result.wait_for_network is False
        assert result.action is not None

        # Test action execution
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert (
            "Successfully navigated to https://example.com"
            in action_result.content[0]["text"]
        )


@pytest.mark.asyncio
async def test_browser_close():
    # Test browser closing functionality
    core_tools = get_core_tools(capture_snapshot=False)
    close_tool = next(
        tool for tool in core_tools if tool.schema.name == "browser_close"
    )

    # Mock service result
    mock_service_result = {"success": True, "message": "Browser closed successfully"}

    # Create mock context
    mock_context = MagicMock()

    with patch.object(CoreService, "close_browser", return_value=mock_service_result):
        result = await close_tool.handle(mock_context, {})

        # Test ToolResult structure
        assert result.code == ["# Close browser"]
        assert result.capture_snapshot is False
        assert result.wait_for_network is False
        assert result.action is not None

        # Test action execution
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert "Browser closed successfully" in action_result.content[0]["text"]


@pytest.mark.asyncio
async def test_browser_resize():
    # Test browser resizing functionality
    core_tools = get_core_tools(capture_snapshot=False)
    resize_tool = next(
        tool for tool in core_tools if tool.schema.name == "browser_resize"
    )

    # Mock service result
    mock_service_result = {
        "success": True,
        "data": {"width": 1920, "height": 1080},
        "message": "Browser resized to 1920x1080",
    }

    # Create mock context
    mock_context = MagicMock()

    with patch.object(CoreService, "resize_browser", return_value=mock_service_result):
        result = await resize_tool.handle(mock_context, {"width": 1920, "height": 1080})

        # Test ToolResult structure
        assert result.code == ["# Resize browser to 1920x1080"]
        assert result.capture_snapshot is False
        assert result.wait_for_network is True
        assert result.action is not None

        # Test action execution
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert "Browser resized to 1920x1080" in action_result.content[0]["text"]


@pytest.mark.asyncio
async def test_browser_navigate_error_handling():
    # Test error handling in navigation
    core_tools = get_core_tools(capture_snapshot=False)
    navigate_tool = next(
        tool for tool in core_tools if tool.schema.name == "browser_navigate"
    )

    # Mock service error result
    mock_service_result = {"success": False, "error": "Invalid URL format"}

    # Create mock context
    mock_context = MagicMock()

    with patch.object(CoreService, "navigate_to_url", return_value=mock_service_result):
        result = await navigate_tool.handle(mock_context, {"url": "invalid-url"})

        # Test action execution with error
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert (
            "Navigation failed: Invalid URL format" in action_result.content[0]["text"]
        )


@pytest.mark.asyncio
async def test_browser_close_error_handling():
    # Test error handling in browser close
    core_tools = get_core_tools(capture_snapshot=False)
    close_tool = next(
        tool for tool in core_tools if tool.schema.name == "browser_close"
    )

    # Mock service error result
    mock_service_result = {"success": False, "error": "No browser instance available"}

    # Create mock context
    mock_context = MagicMock()

    with patch.object(CoreService, "close_browser", return_value=mock_service_result):
        result = await close_tool.handle(mock_context, {})

        # Test action execution with error
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert (
            "Error: No browser instance available" in action_result.content[0]["text"]
        )


@pytest.mark.asyncio
async def test_core_tools_capability_filtering():
    # Test that core tools have proper capability filtering
    core_tools = get_core_tools(capture_snapshot=False)

    # Check that we have the expected core tools
    tool_names = [tool.schema.name for tool in core_tools]
    expected_tools = ["browser_navigate", "browser_close", "browser_resize"]

    for expected_tool in expected_tools:
        assert expected_tool in tool_names, f"Missing core tool: {expected_tool}"

    # Check that tools have CORE or HISTORY capability
    from core.tool_schema import ToolCapability

    for tool in core_tools:
        assert tool.capability in [ToolCapability.CORE, ToolCapability.HISTORY]


@pytest.mark.asyncio
async def test_core_tools_with_different_capture_snapshot():
    # Test that tools respect capture_snapshot parameter
    tools_with_snapshot = get_core_tools(capture_snapshot=True)
    tools_without_snapshot = get_core_tools(capture_snapshot=False)

    # Find navigate tool in both sets
    navigate_with_snapshot = next(
        tool for tool in tools_with_snapshot if tool.schema.name == "browser_navigate"
    )
    navigate_without_snapshot = next(
        tool
        for tool in tools_without_snapshot
        if tool.schema.name == "browser_navigate"
    )

    # Create mock context and service result
    mock_context = MagicMock()
    mock_service_result = {
        "success": True,
        "data": {"url": "https://example.com"},
        "message": "Navigated to https://example.com",
    }

    with patch.object(CoreService, "navigate_to_url", return_value=mock_service_result):
        result_with_snapshot = await navigate_with_snapshot.handle(
            mock_context, {"url": "https://example.com"}
        )
        result_without_snapshot = await navigate_without_snapshot.handle(
            mock_context, {"url": "https://example.com"}
        )

        assert result_with_snapshot.capture_snapshot is True
        assert result_without_snapshot.capture_snapshot is False


@pytest.mark.asyncio
async def test_tool_schema_validation():
    # Test that core tools have proper schema validation
    core_tools = get_core_tools(capture_snapshot=False)

    for tool in core_tools:
        assert tool.schema.name is not None
        assert tool.schema.title is not None
        assert tool.schema.description is not None
        assert tool.schema.input_schema is not None
        assert tool.schema.tool_type is not None
        assert tool.handle is not None
        assert tool.capability is not None
