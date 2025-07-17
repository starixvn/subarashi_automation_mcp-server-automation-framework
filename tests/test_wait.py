import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import sys
from pathlib import Path

# Add the parent directory to the path so we can import from the main package
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.conftest import assert_text_content, assert_contains_text_content
from context import ServerContext
from config.settings import Config, get_default_config, config_to_settings
from tools.wait import get_wait_tools
from services.wait_service import WaitService
from services.base_service import ServiceResult


@pytest.mark.asyncio
async def test_browser_wait_for_text():
    # Test waiting for text to appear
    wait_tools = get_wait_tools(capture_snapshot=False)
    wait_for_tool = next(
        tool for tool in wait_tools if tool.schema.name == "browser_wait_for"
    )

    # Mock service result
    mock_service_result = ServiceResult(
        success=True,
        message="Text 'Loading complete' appeared on page",
        data={"text": "Loading complete", "found": True},
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(WaitService, "wait_for_text", return_value=mock_service_result):
        result = await wait_for_tool.handle(mock_context, {"text": "Loading complete"})

        # Test ToolResult structure
        assert result.code == [
            "# Wait for text 'Loading complete' to appear",
        ]
        assert result.capture_snapshot is False
        assert result.wait_for_network is False
        assert result.action is not None

        # Test action execution
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert "Loading complete" in action_result.content[0]["text"]


@pytest.mark.asyncio
async def test_browser_wait_for_text_gone():
    # Test waiting for text to disappear
    wait_tools = get_wait_tools(capture_snapshot=False)
    wait_for_tool = next(
        tool for tool in wait_tools if tool.schema.name == "browser_wait_for"
    )

    # Mock service result
    mock_service_result = ServiceResult(
        success=True,
        message="Text 'Loading...' disappeared from page",
        data={"text_gone": "Loading...", "disappeared": True},
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(
        WaitService, "wait_for_text_gone", return_value=mock_service_result
    ):
        result = await wait_for_tool.handle(mock_context, {"text_gone": "Loading..."})

        # Test ToolResult structure
        assert result.code == [
            "# Wait for text 'Loading...' to disappear",
        ]
        assert result.capture_snapshot is False
        assert result.wait_for_network is False
        assert result.action is not None

        # Test action execution
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert "Loading..." in action_result.content[0]["text"]


@pytest.mark.asyncio
async def test_browser_wait_for_time():
    # Test waiting for specific time
    wait_tools = get_wait_tools(capture_snapshot=False)
    wait_for_tool = next(
        tool for tool in wait_tools if tool.schema.name == "browser_wait_for"
    )

    # Mock service result
    mock_service_result = ServiceResult(
        success=True,
        message="Waited for 2.5 seconds",
        data={"time": 2.5, "elapsed": 2.5},
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(
        WaitService, "wait_for_timeout", return_value=mock_service_result
    ):
        result = await wait_for_tool.handle(mock_context, {"time": 2.5})

        # Test ToolResult structure
        assert result.code == [
            "# Wait for 2.5 seconds",
        ]
        assert result.capture_snapshot is False
        assert result.wait_for_network is False
        assert result.action is not None

        # Test action execution
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert "2.5 seconds" in action_result.content[0]["text"]


@pytest.mark.asyncio
async def test_browser_wait_for_selector():
    # Test waiting for selector to appear
    wait_tools = get_wait_tools(capture_snapshot=False)
    wait_for_selector_tool = next(
        tool for tool in wait_tools if tool.schema.name == "browser_wait_for_selector"
    )

    # Mock service result
    mock_service_result = ServiceResult(
        success=True,
        message="Element found: #submit-button",
        data={"selector": "#submit-button", "found": True, "timeout": 10},
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(
        WaitService, "wait_for_selector", return_value=mock_service_result
    ):
        result = await wait_for_selector_tool.handle(
            mock_context, {"selector": "#submit-button", "timeout": 10}
        )

        # Test ToolResult structure
        assert result.code == [
            "# Wait for element to appear",
            "# Selector: '#submit-button'",
            "# Timeout: 10.0 seconds",
        ]
        assert result.capture_snapshot is False
        assert result.wait_for_network is False
        assert result.action is not None

        # Test action execution
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert "Element found: #submit-button" in action_result.content[0]["text"]


@pytest.mark.asyncio
async def test_browser_wait_for_selector_with_timeout():
    # Test waiting for selector with custom timeout
    wait_tools = get_wait_tools(capture_snapshot=False)
    wait_for_selector_tool = next(
        tool for tool in wait_tools if tool.schema.name == "browser_wait_for_selector"
    )

    # Mock service result
    mock_service_result = ServiceResult(
        success=True,
        message="Element found: .loading-spinner",
        data={"selector": ".loading-spinner", "found": True, "timeout": 30},
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(
        WaitService, "wait_for_selector", return_value=mock_service_result
    ):
        result = await wait_for_selector_tool.handle(
            mock_context, {"selector": ".loading-spinner", "timeout": 30}
        )

        # Test ToolResult structure
        assert result.code == [
            "# Wait for element to appear",
            "# Selector: '.loading-spinner'",
            "# Timeout: 30.0 seconds",
        ]
        assert result.capture_snapshot is False
        assert result.wait_for_network is False
        assert result.action is not None

        # Test action execution
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert "Element found: .loading-spinner" in action_result.content[0]["text"]


@pytest.mark.asyncio
async def test_browser_wait_for_text_timeout():
    # Test error handling when text wait times out
    wait_tools = get_wait_tools(capture_snapshot=False)
    wait_for_tool = next(
        tool for tool in wait_tools if tool.schema.name == "browser_wait_for"
    )

    # Mock service error result
    mock_service_result = ServiceResult(
        success=False,
        message="Timeout waiting for text 'Non-existent text'",
        error="Timeout",
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(WaitService, "wait_for_text", return_value=mock_service_result):
        result = await wait_for_tool.handle(mock_context, {"text": "Non-existent text"})

        # Test action execution with error
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert (
            "Timeout waiting for text 'Non-existent text'"
            in action_result.content[0]["text"]
        )


@pytest.mark.asyncio
async def test_browser_wait_for_selector_timeout():
    # Test error handling when selector wait times out
    wait_tools = get_wait_tools(capture_snapshot=False)
    wait_for_selector_tool = next(
        tool for tool in wait_tools if tool.schema.name == "browser_wait_for_selector"
    )

    # Mock service error result
    mock_service_result = ServiceResult(
        success=False,
        message="Timeout waiting for selector '#non-existent'",
        error="Timeout",
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(
        WaitService, "wait_for_selector", return_value=mock_service_result
    ):
        result = await wait_for_selector_tool.handle(
            mock_context, {"selector": "#non-existent", "timeout": 5}
        )

        # Test action execution with error
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert (
            "Timeout waiting for selector '#non-existent'"
            in action_result.content[0]["text"]
        )


@pytest.mark.asyncio
async def test_browser_wait_for_multiple_conditions():
    # Test waiting with multiple conditions
    wait_tools = get_wait_tools(capture_snapshot=False)
    wait_for_tool = next(
        tool for tool in wait_tools if tool.schema.name == "browser_wait_for"
    )

    # Mock service results
    mock_service_result = ServiceResult(
        success=True,
        message="Text appeared successfully",
        data={"text": "Success", "found": True},
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(WaitService, "wait_for_text", return_value=mock_service_result):
        result = await wait_for_tool.handle(
            mock_context, {"text": "Success", "time": 1.0}
        )

        # Test ToolResult structure with multiple conditions
        assert result.code == [
            "# Wait for 1.0 seconds",
            "# Wait for text 'Success' to appear",
        ]


@pytest.mark.asyncio
async def test_browser_wait_for_short_time():
    # Test waiting for short time period
    wait_tools = get_wait_tools(capture_snapshot=False)
    wait_for_tool = next(
        tool for tool in wait_tools if tool.schema.name == "browser_wait_for"
    )

    # Mock service result
    mock_service_result = ServiceResult(
        success=True, message="Waited for 0.5 seconds", data={"time": 0.5}
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(
        WaitService, "wait_for_timeout", return_value=mock_service_result
    ):
        result = await wait_for_tool.handle(mock_context, {"time": 0.5})

        # Test ToolResult structure
        assert result.code == ["# Wait for 0.5 seconds"]


@pytest.mark.asyncio
async def test_browser_wait_for_long_time():
    # Test waiting for longer time period
    wait_tools = get_wait_tools(capture_snapshot=False)
    wait_for_tool = next(
        tool for tool in wait_tools if tool.schema.name == "browser_wait_for"
    )

    # Mock service result
    mock_service_result = ServiceResult(
        success=True, message="Waited for 30 seconds", data={"time": 30}
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(
        WaitService, "wait_for_timeout", return_value=mock_service_result
    ):
        result = await wait_for_tool.handle(mock_context, {"time": 30})

        # Test ToolResult structure
        assert result.code == ["# Wait for 30.0 seconds"]


@pytest.mark.asyncio
async def test_wait_capability_filtering():
    # Test that wait tools have proper capability filtering
    wait_tools = get_wait_tools(capture_snapshot=False)

    # Check that we have the expected wait tools
    tool_names = [tool.schema.name for tool in wait_tools]
    expected_tools = ["browser_wait_for", "browser_wait_for_selector"]

    for expected_tool in expected_tools:
        assert expected_tool in tool_names, f"Missing wait tool: {expected_tool}"

    # Check that all tools have WAIT capability
    from core.tool_schema import ToolCapability

    for tool in wait_tools:
        assert tool.capability == ToolCapability.WAIT


@pytest.mark.asyncio
async def test_wait_tools_capture_snapshot_parameter():
    # Test that wait tools respect capture_snapshot parameter
    tools_with_snapshot = get_wait_tools(capture_snapshot=True)
    tools_without_snapshot = get_wait_tools(capture_snapshot=False)

    # Find wait for tool in both sets
    wait_for_with_snapshot = next(
        tool for tool in tools_with_snapshot if tool.schema.name == "browser_wait_for"
    )
    wait_for_without_snapshot = next(
        tool
        for tool in tools_without_snapshot
        if tool.schema.name == "browser_wait_for"
    )

    # Create mock context and service result
    mock_context = MagicMock()
    mock_service_result = ServiceResult(
        success=True,
        message="Waited successfully",
        data={"time": 1.0, "elapsed": 1.0},
    )

    with patch.object(
        WaitService, "wait_for_timeout", return_value=mock_service_result
    ):
        result_with_snapshot = await wait_for_with_snapshot.handle(
            mock_context, {"time": 1.0}
        )
        result_without_snapshot = await wait_for_without_snapshot.handle(
            mock_context, {"time": 1.0}
        )

        assert result_with_snapshot.capture_snapshot is True
        assert result_without_snapshot.capture_snapshot is False


@pytest.mark.asyncio
async def test_wait_tools_schema_validation():
    # Test that wait tools have proper schema validation
    wait_tools = get_wait_tools(capture_snapshot=False)

    for tool in wait_tools:
        assert tool.schema.name is not None
        assert tool.schema.title is not None
        assert tool.schema.description is not None
        assert tool.schema.input_schema is not None
        assert tool.schema.tool_type is not None
        assert tool.handle is not None
        assert tool.capability is not None

        # Test that wait tools have read-only type
        from core.tool_schema import ToolType

        assert tool.schema.tool_type == ToolType.READ_ONLY


@pytest.mark.asyncio
async def test_wait_tools_network_settings():
    # Test that wait tools have proper network settings
    wait_tools = get_wait_tools(capture_snapshot=False)

    for tool in wait_tools:
        mock_context = MagicMock()
        mock_service_result = ServiceResult(
            success=True, message="Wait completed", data={}
        )

        with patch.object(
            WaitService, "wait_for_timeout", return_value=mock_service_result
        ):
            with patch.object(
                WaitService, "wait_for_text", return_value=mock_service_result
            ):
                with patch.object(
                    WaitService, "wait_for_selector", return_value=mock_service_result
                ):
                    if tool.schema.name == "browser_wait_for":
                        result = await tool.handle(mock_context, {"time": 1.0})
                    else:
                        result = await tool.handle(
                            mock_context, {"selector": "#test", "timeout": 10}
                        )

                    # Wait operations shouldn't wait for network
                    assert result.wait_for_network is False
