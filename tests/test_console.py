import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import sys
from pathlib import Path

# Add the parent directory to the path so we can import from the main package
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.conftest import assert_text_content, assert_contains_text_content
from context import ServerContext
from config.settings import Config, get_default_config, config_to_settings
from tools.console import get_console_tools
from services.console_service import ConsoleService
from services.base_service import ServiceResult


@pytest.mark.asyncio
async def test_browser_console_clear():
    # Test console clear functionality
    console_tools = get_console_tools(capture_snapshot=False)
    clear_tool = next(
        tool for tool in console_tools if tool.schema.name == "browser_console_clear"
    )

    # Mock service result
    mock_service_result = ServiceResult(
        success=True,
        message="Console cleared successfully",
        data={"messages_cleared": 5},
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(
        ConsoleService, "clear_console", return_value=mock_service_result
    ):
        result = await clear_tool.handle(mock_context, {})

        # Test ToolResult structure
        assert result.code == [
            "# Clear browser console messages",
            "# Removes all console entries",
        ]
        assert result.capture_snapshot is False
        assert result.wait_for_network is False
        assert result.action is not None

        # Test action execution
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert "Console cleared successfully" in action_result.content[0]["text"]


@pytest.mark.asyncio
async def test_browser_console_messages():
    # Test console message retrieval
    console_tools = get_console_tools(capture_snapshot=False)
    messages_tool = next(
        tool for tool in console_tools if tool.schema.name == "browser_console_messages"
    )

    # Mock service result with console messages
    mock_service_result = ServiceResult(
        success=True,
        message="Retrieved 3 console messages",
        data={
            "messages": [
                {"type": "log", "text": "Application started successfully"},
                {"type": "warn", "text": "Deprecated API usage detected"},
                {
                    "type": "error",
                    "text": "Failed to load resource: https://example.com/missing.js",
                },
            ],
            "count": 3,
        },
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(
        ConsoleService, "get_console_messages", return_value=mock_service_result
    ):
        result = await messages_tool.handle(mock_context, {})

        # Test ToolResult structure
        assert result.code == [
            "# Get browser console messages",
            "# Returns all console entries (log, warn, error, etc.)",
        ]
        assert result.capture_snapshot is False
        assert result.wait_for_network is False
        assert result.action is not None

        # Test action execution
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        content_text = action_result.content[0]["text"]
        assert "### Console Messages" in content_text
        assert "**log**: Application started successfully" in content_text
        assert "**warn**: Deprecated API usage detected" in content_text
        assert (
            "**error**: Failed to load resource: https://example.com/missing.js"
            in content_text
        )


@pytest.mark.asyncio
async def test_browser_console_messages_empty():
    # Test console message retrieval when no messages exist
    console_tools = get_console_tools(capture_snapshot=False)
    messages_tool = next(
        tool for tool in console_tools if tool.schema.name == "browser_console_messages"
    )

    # Mock service result with no messages
    mock_service_result = ServiceResult(
        success=True,
        message="No console messages found",
        data={"messages": [], "count": 0},
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(
        ConsoleService, "get_console_messages", return_value=mock_service_result
    ):
        result = await messages_tool.handle(mock_context, {})

        # Test action execution
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert "No console messages" in action_result.content[0]["text"]


@pytest.mark.asyncio
async def test_browser_console_messages_with_filters():
    # Test console message retrieval with filtering
    console_tools = get_console_tools(capture_snapshot=False)
    messages_tool = next(
        tool for tool in console_tools if tool.schema.name == "browser_console_messages"
    )

    # Mock service result with filtered messages
    mock_service_result = ServiceResult(
        success=True,
        message="Retrieved 2 error messages",
        data={
            "messages": [
                {"type": "error", "text": "Network error occurred"},
                {"type": "error", "text": "Validation failed"},
            ],
            "count": 2,
            "filter": "error",
        },
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(
        ConsoleService, "get_console_messages", return_value=mock_service_result
    ):
        result = await messages_tool.handle(mock_context, {"filter": "error"})

        # Test action execution
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        content_text = action_result.content[0]["text"]
        assert "### Console Messages" in content_text
        assert "**error**: Network error occurred" in content_text
        assert "**error**: Validation failed" in content_text


@pytest.mark.asyncio
async def test_browser_console_clear_error():
    # Test error handling in console clear
    console_tools = get_console_tools(capture_snapshot=False)
    clear_tool = next(
        tool for tool in console_tools if tool.schema.name == "browser_console_clear"
    )

    # Mock service error result
    mock_service_result = ServiceResult(
        success=False, message="Failed to clear console", error="Browser not available"
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(
        ConsoleService, "clear_console", return_value=mock_service_result
    ):
        result = await clear_tool.handle(mock_context, {})

        # Test action execution with error
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert "Failed to clear console" in action_result.content[0]["text"]


@pytest.mark.asyncio
async def test_browser_console_messages_error():
    # Test error handling in console messages retrieval
    console_tools = get_console_tools(capture_snapshot=False)
    messages_tool = next(
        tool for tool in console_tools if tool.schema.name == "browser_console_messages"
    )

    # Mock service error result
    mock_service_result = ServiceResult(
        success=False,
        message="Failed to retrieve console messages",
        error="Page not loaded",
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(
        ConsoleService, "get_console_messages", return_value=mock_service_result
    ):
        result = await messages_tool.handle(mock_context, {})

        # Test action execution with error
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert "Failed to retrieve console messages" in action_result.content[0]["text"]


@pytest.mark.asyncio
async def test_console_capability_filtering():
    # Test that console tools have proper capability filtering
    console_tools = get_console_tools(capture_snapshot=False)

    # Check that we have the expected console tools
    tool_names = [tool.schema.name for tool in console_tools]
    expected_tools = ["browser_console_clear", "browser_console_messages"]

    for expected_tool in expected_tools:
        assert expected_tool in tool_names, f"Missing console tool: {expected_tool}"

    # Check that all tools have CONSOLE capability
    from core.tool_schema import ToolCapability

    for tool in console_tools:
        assert tool.capability == ToolCapability.CONSOLE


@pytest.mark.asyncio
async def test_console_tools_capture_snapshot_parameter():
    # Test that console tools respect capture_snapshot parameter
    tools_with_snapshot = get_console_tools(capture_snapshot=True)
    tools_without_snapshot = get_console_tools(capture_snapshot=False)

    # Find clear tool in both sets
    clear_with_snapshot = next(
        tool
        for tool in tools_with_snapshot
        if tool.schema.name == "browser_console_clear"
    )
    clear_without_snapshot = next(
        tool
        for tool in tools_without_snapshot
        if tool.schema.name == "browser_console_clear"
    )

    # Create mock context and service result
    mock_context = MagicMock()
    mock_service_result = ServiceResult(
        success=True,
        message="Console cleared successfully",
        data={"messages_cleared": 0},
    )

    with patch.object(
        ConsoleService, "clear_console", return_value=mock_service_result
    ):
        result_with_snapshot = await clear_with_snapshot.handle(mock_context, {})
        result_without_snapshot = await clear_without_snapshot.handle(mock_context, {})

        assert result_with_snapshot.capture_snapshot is True
        assert result_without_snapshot.capture_snapshot is False


@pytest.mark.asyncio
async def test_console_tools_schema_validation():
    # Test that console tools have proper schema validation
    console_tools = get_console_tools(capture_snapshot=False)

    for tool in console_tools:
        assert tool.schema.name is not None
        assert tool.schema.title is not None
        assert tool.schema.description is not None
        assert tool.schema.input_schema is not None
        assert tool.schema.tool_type is not None
        assert tool.handle is not None
        assert tool.capability is not None

        # Test that tools have proper type
        from core.tool_schema import ToolType

        if tool.schema.name == "browser_console_clear":
            assert tool.schema.tool_type == ToolType.READ_ONLY
        elif tool.schema.name == "browser_console_messages":
            assert tool.schema.tool_type == ToolType.READ_ONLY


@pytest.mark.asyncio
async def test_console_tools_network_settings():
    # Test that console tools have proper network settings
    console_tools = get_console_tools(capture_snapshot=False)

    for tool in console_tools:
        mock_context = MagicMock()
        mock_service_result = ServiceResult(
            success=True, message="Operation successful", data={}
        )

        with patch.object(
            ConsoleService, "clear_console", return_value=mock_service_result
        ):
            with patch.object(
                ConsoleService, "get_console_messages", return_value=mock_service_result
            ):
                result = await tool.handle(mock_context, {})

                # Console operations shouldn't wait for network
                assert result.wait_for_network is False


@pytest.mark.asyncio
async def test_console_messages_detailed_formatting():
    # Test detailed console message formatting
    console_tools = get_console_tools(capture_snapshot=False)
    messages_tool = next(
        tool for tool in console_tools if tool.schema.name == "browser_console_messages"
    )

    # Mock service result with detailed messages
    mock_service_result = ServiceResult(
        success=True,
        message="Retrieved console messages with details",
        data={
            "messages": [
                {
                    "type": "log",
                    "text": "User logged in",
                    "timestamp": "2024-01-01T10:00:00Z",
                    "source": "main.js:123",
                },
                {
                    "type": "warn",
                    "text": "Slow network detected",
                    "timestamp": "2024-01-01T10:00:01Z",
                    "source": "network.js:456",
                },
            ],
            "count": 2,
            "detailed": True,
        },
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(
        ConsoleService, "get_console_messages", return_value=mock_service_result
    ):
        result = await messages_tool.handle(mock_context, {"detailed": True})

        # Test action execution
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        content_text = action_result.content[0]["text"]
        assert "### Console Messages" in content_text
        assert "**log**: User logged in" in content_text
        assert "**warn**: Slow network detected" in content_text
