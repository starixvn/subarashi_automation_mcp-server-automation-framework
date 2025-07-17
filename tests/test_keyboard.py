import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import sys
from pathlib import Path

# Add the parent directory to the path so we can import from the main package
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.conftest import assert_text_content, assert_contains_text_content
from context import ServerContext
from config.settings import Config, get_default_config, config_to_settings
from tools.keyboard import get_keyboard_tools
from services.keyboard_service import KeyboardService
from services.base_service import ServiceResult


@pytest.mark.asyncio
async def test_browser_press_key_single():
    # Test single key press
    keyboard_tools = get_keyboard_tools(capture_snapshot=True)
    press_key_tool = next(
        tool for tool in keyboard_tools if tool.schema.name == "browser_press_key"
    )

    # Mock service result
    mock_service_result = ServiceResult(
        success=True,
        message="Successfully pressed key: Enter",
        data={"key": "Enter", "modifiers": []},
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(KeyboardService, "press_key", return_value=mock_service_result):
        result = await press_key_tool.handle(mock_context, {"key": "Enter"})

        # Test ToolResult structure
        assert result.code == [
            "# Press key on keyboard",
            "# Key: 'Enter'",
        ]
        assert result.capture_snapshot is True
        assert result.wait_for_network is True
        assert result.action is not None

        # Test action execution
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert "Successfully pressed key: Enter" in action_result.content[0]["text"]


@pytest.mark.asyncio
async def test_browser_press_key_escape():
    # Test escape key press
    keyboard_tools = get_keyboard_tools(capture_snapshot=True)
    press_key_tool = next(
        tool for tool in keyboard_tools if tool.schema.name == "browser_press_key"
    )

    # Mock service result
    mock_service_result = ServiceResult(
        success=True,
        message="Successfully pressed key: Escape",
        data={"key": "Escape", "modifiers": []},
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(KeyboardService, "press_key", return_value=mock_service_result):
        result = await press_key_tool.handle(mock_context, {"key": "Escape"})

        # Test ToolResult structure
        assert result.code == [
            "# Press key on keyboard",
            "# Key: 'Escape'",
        ]
        assert result.capture_snapshot is True
        assert result.wait_for_network is True
        assert result.action is not None

        # Test action execution
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert "Successfully pressed key: Escape" in action_result.content[0]["text"]


@pytest.mark.asyncio
async def test_browser_press_key_tab():
    # Test tab key press
    keyboard_tools = get_keyboard_tools(capture_snapshot=True)
    press_key_tool = next(
        tool for tool in keyboard_tools if tool.schema.name == "browser_press_key"
    )

    # Mock service result
    mock_service_result = ServiceResult(
        success=True,
        message="Successfully pressed key: Tab",
        data={"key": "Tab", "modifiers": []},
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(KeyboardService, "press_key", return_value=mock_service_result):
        result = await press_key_tool.handle(mock_context, {"key": "Tab"})

        # Test ToolResult structure
        assert result.code == [
            "# Press key on keyboard",
            "# Key: 'Tab'",
        ]
        assert result.capture_snapshot is True
        assert result.wait_for_network is True
        assert result.action is not None

        # Test action execution
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert "Successfully pressed key: Tab" in action_result.content[0]["text"]


@pytest.mark.asyncio
async def test_browser_press_key_shift_tab():
    # Test shift+tab key combination
    keyboard_tools = get_keyboard_tools(capture_snapshot=True)
    press_key_tool = next(
        tool for tool in keyboard_tools if tool.schema.name == "browser_press_key"
    )

    # Mock service result
    mock_service_result = ServiceResult(
        success=True,
        message="Successfully pressed key: Shift+Tab",
        data={"key": "Shift+Tab", "modifiers": ["Shift"]},
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(KeyboardService, "press_key", return_value=mock_service_result):
        result = await press_key_tool.handle(mock_context, {"key": "Shift+Tab"})

        # Test ToolResult structure
        assert result.code == [
            "# Press key on keyboard",
            "# Key: 'Shift+Tab'",
        ]
        assert result.capture_snapshot is True
        assert result.wait_for_network is True
        assert result.action is not None

        # Test action execution
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert "Successfully pressed key: Shift+Tab" in action_result.content[0]["text"]


@pytest.mark.asyncio
async def test_browser_press_key_ctrl_a():
    # Test control+a key combination
    keyboard_tools = get_keyboard_tools(capture_snapshot=True)
    press_key_tool = next(
        tool for tool in keyboard_tools if tool.schema.name == "browser_press_key"
    )

    # Mock service result
    mock_service_result = ServiceResult(
        success=True,
        message="Successfully pressed key: Control+a",
        data={"key": "Control+a", "modifiers": ["Control"]},
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(KeyboardService, "press_key", return_value=mock_service_result):
        result = await press_key_tool.handle(mock_context, {"key": "Control+a"})

        # Test ToolResult structure
        assert result.code == [
            "# Press key on keyboard",
            "# Key: 'Control+a'",
        ]
        assert result.capture_snapshot is True
        assert result.wait_for_network is True
        assert result.action is not None

        # Test action execution
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert "Successfully pressed key: Control+a" in action_result.content[0]["text"]


@pytest.mark.asyncio
async def test_browser_press_key_character():
    # Test character key press
    keyboard_tools = get_keyboard_tools(capture_snapshot=True)
    press_key_tool = next(
        tool for tool in keyboard_tools if tool.schema.name == "browser_press_key"
    )

    # Mock service result
    mock_service_result = ServiceResult(
        success=True,
        message="Successfully pressed key: a",
        data={"key": "a", "modifiers": []},
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(KeyboardService, "press_key", return_value=mock_service_result):
        result = await press_key_tool.handle(mock_context, {"key": "a"})

        # Test ToolResult structure
        assert result.code == [
            "# Press key on keyboard",
            "# Key: 'a'",
        ]
        assert result.capture_snapshot is True
        assert result.wait_for_network is True
        assert result.action is not None

        # Test action execution
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert "Successfully pressed key: a" in action_result.content[0]["text"]


@pytest.mark.asyncio
async def test_browser_press_key_arrow_keys():
    # Test arrow key presses
    keyboard_tools = get_keyboard_tools(capture_snapshot=True)
    press_key_tool = next(
        tool for tool in keyboard_tools if tool.schema.name == "browser_press_key"
    )

    arrow_keys = ["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight"]

    for key in arrow_keys:
        # Mock service result
        mock_service_result = ServiceResult(
            success=True,
            message=f"Successfully pressed key: {key}",
            data={"key": key, "modifiers": []},
        )

        # Create mock context
        mock_context = MagicMock()

        with patch.object(
            KeyboardService, "press_key", return_value=mock_service_result
        ):
            result = await press_key_tool.handle(mock_context, {"key": key})

            # Test ToolResult structure
            assert result.code == [
                "# Press key on keyboard",
                f"# Key: '{key}'",
            ]
            assert result.capture_snapshot is True
            assert result.wait_for_network is True
            assert result.action is not None

            # Test action execution
            action_result = await result.action()
            assert action_result.content[0]["type"] == "text"
            assert (
                f"Successfully pressed key: {key}" in action_result.content[0]["text"]
            )


@pytest.mark.asyncio
async def test_browser_press_key_function_keys():
    # Test function key presses
    keyboard_tools = get_keyboard_tools(capture_snapshot=True)
    press_key_tool = next(
        tool for tool in keyboard_tools if tool.schema.name == "browser_press_key"
    )

    function_keys = ["F1", "F5", "F12"]

    for key in function_keys:
        # Mock service result
        mock_service_result = ServiceResult(
            success=True,
            message=f"Successfully pressed key: {key}",
            data={"key": key, "modifiers": []},
        )

        # Create mock context
        mock_context = MagicMock()

        with patch.object(
            KeyboardService, "press_key", return_value=mock_service_result
        ):
            result = await press_key_tool.handle(mock_context, {"key": key})

            # Test ToolResult structure
            assert result.code == [
                "# Press key on keyboard",
                f"# Key: '{key}'",
            ]
            assert result.capture_snapshot is True
            assert result.wait_for_network is True
            assert result.action is not None

            # Test action execution
            action_result = await result.action()
            assert action_result.content[0]["type"] == "text"
            assert (
                f"Successfully pressed key: {key}" in action_result.content[0]["text"]
            )


@pytest.mark.asyncio
async def test_browser_press_key_error_handling():
    # Test error handling for invalid key
    keyboard_tools = get_keyboard_tools(capture_snapshot=True)
    press_key_tool = next(
        tool for tool in keyboard_tools if tool.schema.name == "browser_press_key"
    )

    # Mock service error result
    mock_service_result = ServiceResult(
        success=False, message="Invalid key: InvalidKey", error="Invalid key"
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(KeyboardService, "press_key", return_value=mock_service_result):
        result = await press_key_tool.handle(mock_context, {"key": "InvalidKey"})

        # Test action execution with error
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert "Invalid key: InvalidKey" in action_result.content[0]["text"]


@pytest.mark.asyncio
async def test_browser_press_key_page_navigation():
    # Test page navigation keys
    keyboard_tools = get_keyboard_tools(capture_snapshot=True)
    press_key_tool = next(
        tool for tool in keyboard_tools if tool.schema.name == "browser_press_key"
    )

    navigation_keys = ["PageUp", "PageDown", "Home", "End"]

    for key in navigation_keys:
        # Mock service result
        mock_service_result = ServiceResult(
            success=True,
            message=f"Successfully pressed key: {key}",
            data={"key": key, "modifiers": []},
        )

        # Create mock context
        mock_context = MagicMock()

        with patch.object(
            KeyboardService, "press_key", return_value=mock_service_result
        ):
            result = await press_key_tool.handle(mock_context, {"key": key})

            # Test action execution
            action_result = await result.action()
            assert action_result.content[0]["type"] == "text"
            assert (
                f"Successfully pressed key: {key}" in action_result.content[0]["text"]
            )


@pytest.mark.asyncio
async def test_keyboard_capability_filtering():
    # Test that keyboard tools have proper capability filtering
    keyboard_tools = get_keyboard_tools(capture_snapshot=True)

    # Check that we have the expected keyboard tools
    tool_names = [tool.schema.name for tool in keyboard_tools]
    expected_tools = ["browser_press_key"]

    for expected_tool in expected_tools:
        assert expected_tool in tool_names, f"Missing keyboard tool: {expected_tool}"

    # Check that all tools have KEYBOARD capability
    from core.tool_schema import ToolCapability

    for tool in keyboard_tools:
        assert tool.capability == ToolCapability.KEYBOARD


@pytest.mark.asyncio
async def test_keyboard_tools_capture_snapshot_parameter():
    # Test that keyboard tools respect capture_snapshot parameter
    tools_with_snapshot = get_keyboard_tools(capture_snapshot=True)
    tools_without_snapshot = get_keyboard_tools(capture_snapshot=False)

    # Find press key tool in both sets
    press_key_with_snapshot = next(
        tool for tool in tools_with_snapshot if tool.schema.name == "browser_press_key"
    )
    press_key_without_snapshot = next(
        tool
        for tool in tools_without_snapshot
        if tool.schema.name == "browser_press_key"
    )

    # Create mock context and service result
    mock_context = MagicMock()
    mock_service_result = ServiceResult(
        success=True,
        message="Successfully pressed key: Enter",
        data={"key": "Enter", "modifiers": []},
    )

    with patch.object(KeyboardService, "press_key", return_value=mock_service_result):
        result_with_snapshot = await press_key_with_snapshot.handle(
            mock_context, {"key": "Enter"}
        )
        result_without_snapshot = await press_key_without_snapshot.handle(
            mock_context, {"key": "Enter"}
        )

        assert result_with_snapshot.capture_snapshot is True
        assert result_without_snapshot.capture_snapshot is False


@pytest.mark.asyncio
async def test_keyboard_tools_schema_validation():
    # Test that keyboard tools have proper schema validation
    keyboard_tools = get_keyboard_tools(capture_snapshot=True)

    for tool in keyboard_tools:
        assert tool.schema.name is not None
        assert tool.schema.title is not None
        assert tool.schema.description is not None
        assert tool.schema.input_schema is not None
        assert tool.schema.tool_type is not None
        assert tool.handle is not None
        assert tool.capability is not None

        # Test that keyboard tools have destructive type (they change page state)
        from core.tool_schema import ToolType

        assert tool.schema.tool_type == ToolType.DESTRUCTIVE


@pytest.mark.asyncio
async def test_keyboard_tools_network_settings():
    # Test that keyboard tools have proper network settings
    keyboard_tools = get_keyboard_tools(capture_snapshot=True)

    for tool in keyboard_tools:
        mock_context = MagicMock()
        mock_service_result = ServiceResult(
            success=True, message="Key pressed successfully", data={"key": "Enter"}
        )

        with patch.object(
            KeyboardService, "press_key", return_value=mock_service_result
        ):
            result = await tool.handle(mock_context, {"key": "Enter"})

            # Keyboard operations should wait for network
            assert result.wait_for_network is True
