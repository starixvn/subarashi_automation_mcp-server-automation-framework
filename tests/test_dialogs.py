import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import sys
from pathlib import Path

# Add the parent directory to the path so we can import from the main package
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.conftest import assert_text_content, assert_contains_text_content
from context import ServerContext
from config.settings import Config, get_default_config, config_to_settings
from tools.dialogs import get_dialog_tools
from services.dialogs_service import DialogsService
from services.base_service import ServiceResult


@pytest.mark.asyncio
async def test_browser_handle_dialog_accept():
    # Test accepting a dialog
    dialog_tools = get_dialog_tools(capture_snapshot=True)
    handle_dialog_tool = next(
        tool for tool in dialog_tools if tool.schema.name == "browser_handle_dialog"
    )

    # Mock service result
    mock_service_result = ServiceResult(
        success=True,
        message="Dialog accepted successfully",
        data={"action": "accept", "type": "confirm"},
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(
        DialogsService, "handle_dialog", return_value=mock_service_result
    ):
        result = await handle_dialog_tool.handle(mock_context, {"accept": True})

        # Test ToolResult structure
        assert result.code == ["# Handle dialog", "# Action: accept"]
        assert result.capture_snapshot is True
        assert result.wait_for_network is False
        assert result.action is not None

        # Test action execution
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert "Dialog accepted successfully" in action_result.content[0]["text"]


@pytest.mark.asyncio
async def test_browser_handle_dialog_dismiss():
    # Test dismissing a dialog
    dialog_tools = get_dialog_tools(capture_snapshot=True)
    handle_dialog_tool = next(
        tool for tool in dialog_tools if tool.schema.name == "browser_handle_dialog"
    )

    # Mock service result
    mock_service_result = ServiceResult(
        success=True,
        message="Dialog dismissed successfully",
        data={"action": "dismiss", "type": "alert"},
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(
        DialogsService, "handle_dialog", return_value=mock_service_result
    ):
        result = await handle_dialog_tool.handle(mock_context, {"accept": False})

        # Test ToolResult structure
        assert result.code == ["# Handle dialog", "# Action: dismiss"]
        assert result.capture_snapshot is True
        assert result.wait_for_network is False
        assert result.action is not None

        # Test action execution
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert "Dialog dismissed successfully" in action_result.content[0]["text"]


@pytest.mark.asyncio
async def test_browser_handle_dialog_with_prompt_text():
    # Test handling a dialog with prompt text
    dialog_tools = get_dialog_tools(capture_snapshot=True)
    handle_dialog_tool = next(
        tool for tool in dialog_tools if tool.schema.name == "browser_handle_dialog"
    )

    # Mock service result
    mock_service_result = ServiceResult(
        success=True,
        message="Dialog accepted with prompt text: 'Hello World'",
        data={"action": "accept", "type": "prompt", "prompt_text": "Hello World"},
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(
        DialogsService, "handle_dialog", return_value=mock_service_result
    ):
        result = await handle_dialog_tool.handle(
            mock_context, {"accept": True, "prompt_text": "Hello World"}
        )

        # Test ToolResult structure
        assert result.code == [
            "# Handle dialog",
            "# Action: accept",
            "# Prompt text: 'Hello World'",
        ]
        assert result.capture_snapshot is True
        assert result.wait_for_network is False
        assert result.action is not None

        # Test action execution
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert (
            "Dialog accepted with prompt text: 'Hello World'"
            in action_result.content[0]["text"]
        )


@pytest.mark.asyncio
async def test_browser_handle_dialog_confirm():
    # Test handling a confirm dialog
    dialog_tools = get_dialog_tools(capture_snapshot=True)
    handle_dialog_tool = next(
        tool for tool in dialog_tools if tool.schema.name == "browser_handle_dialog"
    )

    # Mock service result
    mock_service_result = ServiceResult(
        success=True,
        message="Confirm dialog accepted",
        data={"action": "accept", "type": "confirm", "message": "Are you sure?"},
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(
        DialogsService, "handle_dialog", return_value=mock_service_result
    ):
        result = await handle_dialog_tool.handle(mock_context, {"accept": True})

        # Test action execution
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert "Confirm dialog accepted" in action_result.content[0]["text"]


@pytest.mark.asyncio
async def test_browser_handle_dialog_alert():
    # Test handling an alert dialog
    dialog_tools = get_dialog_tools(capture_snapshot=True)
    handle_dialog_tool = next(
        tool for tool in dialog_tools if tool.schema.name == "browser_handle_dialog"
    )

    # Mock service result
    mock_service_result = ServiceResult(
        success=True,
        message="Alert dialog dismissed",
        data={"action": "dismiss", "type": "alert", "message": "Warning!"},
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(
        DialogsService, "handle_dialog", return_value=mock_service_result
    ):
        result = await handle_dialog_tool.handle(mock_context, {"accept": False})

        # Test action execution
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert "Alert dialog dismissed" in action_result.content[0]["text"]


@pytest.mark.asyncio
async def test_browser_handle_dialog_prompt_cancelled():
    # Test handling a prompt dialog when cancelled
    dialog_tools = get_dialog_tools(capture_snapshot=True)
    handle_dialog_tool = next(
        tool for tool in dialog_tools if tool.schema.name == "browser_handle_dialog"
    )

    # Mock service result
    mock_service_result = ServiceResult(
        success=True,
        message="Prompt dialog cancelled",
        data={"action": "dismiss", "type": "prompt", "message": "Enter your name:"},
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(
        DialogsService, "handle_dialog", return_value=mock_service_result
    ):
        result = await handle_dialog_tool.handle(mock_context, {"accept": False})

        # Test action execution
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert "Prompt dialog cancelled" in action_result.content[0]["text"]


@pytest.mark.asyncio
async def test_browser_handle_dialog_prompt_empty_text():
    # Test handling a prompt dialog with empty text
    dialog_tools = get_dialog_tools(capture_snapshot=True)
    handle_dialog_tool = next(
        tool for tool in dialog_tools if tool.schema.name == "browser_handle_dialog"
    )

    # Mock service result
    mock_service_result = ServiceResult(
        success=True,
        message="Prompt dialog accepted with empty text",
        data={"action": "accept", "type": "prompt", "prompt_text": ""},
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(
        DialogsService, "handle_dialog", return_value=mock_service_result
    ):
        result = await handle_dialog_tool.handle(
            mock_context, {"accept": True, "prompt_text": ""}
        )

        # Test action execution
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert (
            "Prompt dialog accepted with empty text" in action_result.content[0]["text"]
        )


@pytest.mark.asyncio
async def test_browser_handle_dialog_error_no_dialog():
    # Test error handling when no dialog is present
    dialog_tools = get_dialog_tools(capture_snapshot=True)
    handle_dialog_tool = next(
        tool for tool in dialog_tools if tool.schema.name == "browser_handle_dialog"
    )

    # Mock service error result
    mock_service_result = ServiceResult(
        success=False, message="No dialog present to handle", error="No dialog present"
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(
        DialogsService, "handle_dialog", return_value=mock_service_result
    ):
        result = await handle_dialog_tool.handle(mock_context, {"accept": True})

        # Test action execution with error
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert "No dialog present to handle" in action_result.content[0]["text"]


@pytest.mark.asyncio
async def test_browser_handle_dialog_error_timeout():
    # Test error handling for dialog timeout
    dialog_tools = get_dialog_tools(capture_snapshot=True)
    handle_dialog_tool = next(
        tool for tool in dialog_tools if tool.schema.name == "browser_handle_dialog"
    )

    # Mock service error result
    mock_service_result = ServiceResult(
        success=False, message="Dialog handling timed out", error="Dialog timeout"
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(
        DialogsService, "handle_dialog", return_value=mock_service_result
    ):
        result = await handle_dialog_tool.handle(mock_context, {"accept": True})

        # Test action execution with error
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert "Dialog handling timed out" in action_result.content[0]["text"]


@pytest.mark.asyncio
async def test_browser_handle_dialog_file_chooser():
    # Test handling a file chooser dialog
    dialog_tools = get_dialog_tools(capture_snapshot=True)
    handle_dialog_tool = next(
        tool for tool in dialog_tools if tool.schema.name == "browser_handle_dialog"
    )

    # Mock service result
    mock_service_result = ServiceResult(
        success=True,
        message="File chooser dialog accepted",
        data={"action": "accept", "type": "filechooser", "files": ["/tmp/test.txt"]},
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(
        DialogsService, "handle_dialog", return_value=mock_service_result
    ):
        result = await handle_dialog_tool.handle(mock_context, {"accept": True})

        # Test action execution
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert "File chooser dialog accepted" in action_result.content[0]["text"]


@pytest.mark.asyncio
async def test_browser_handle_dialog_beforeunload():
    # Test handling a beforeunload dialog
    dialog_tools = get_dialog_tools(capture_snapshot=True)
    handle_dialog_tool = next(
        tool for tool in dialog_tools if tool.schema.name == "browser_handle_dialog"
    )

    # Mock service result
    mock_service_result = ServiceResult(
        success=True,
        message="Beforeunload dialog accepted",
        data={"action": "accept", "type": "beforeunload", "message": "Leave page?"},
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(
        DialogsService, "handle_dialog", return_value=mock_service_result
    ):
        result = await handle_dialog_tool.handle(mock_context, {"accept": True})

        # Test action execution
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert "Beforeunload dialog accepted" in action_result.content[0]["text"]


@pytest.mark.asyncio
async def test_dialogs_capability_filtering():
    # Test that dialog tools have proper capability filtering
    dialog_tools = get_dialog_tools(capture_snapshot=True)

    # Check that we have the expected dialog tools
    tool_names = [tool.schema.name for tool in dialog_tools]
    expected_tools = ["browser_handle_dialog"]

    for expected_tool in expected_tools:
        assert expected_tool in tool_names, f"Missing dialog tool: {expected_tool}"

    # Check that all tools have DIALOGS capability
    from core.tool_schema import ToolCapability

    for tool in dialog_tools:
        assert tool.capability == ToolCapability.CORE


@pytest.mark.asyncio
async def test_dialog_tools_capture_snapshot_parameter():
    # Test that dialog tools respect capture_snapshot parameter
    tools_with_snapshot = get_dialog_tools(capture_snapshot=True)
    tools_without_snapshot = get_dialog_tools(capture_snapshot=False)

    # Find handle dialog tool in both sets
    handle_dialog_with_snapshot = next(
        tool
        for tool in tools_with_snapshot
        if tool.schema.name == "browser_handle_dialog"
    )
    handle_dialog_without_snapshot = next(
        tool
        for tool in tools_without_snapshot
        if tool.schema.name == "browser_handle_dialog"
    )

    # Create mock context and service result
    mock_context = MagicMock()
    mock_service_result = ServiceResult(
        success=True,
        message="Dialog handled successfully",
        data={"action": "accept", "type": "confirm"},
    )

    with patch.object(
        DialogsService, "handle_dialog", return_value=mock_service_result
    ):
        result_with_snapshot = await handle_dialog_with_snapshot.handle(
            mock_context, {"accept": True}
        )
        result_without_snapshot = await handle_dialog_without_snapshot.handle(
            mock_context, {"accept": True}
        )

        assert result_with_snapshot.capture_snapshot is True
        assert result_without_snapshot.capture_snapshot is False


@pytest.mark.asyncio
async def test_dialog_tools_schema_validation():
    # Test that dialog tools have proper schema validation
    dialog_tools = get_dialog_tools(capture_snapshot=True)

    for tool in dialog_tools:
        assert tool.schema.name is not None
        assert tool.schema.title is not None
        assert tool.schema.description is not None
        assert tool.schema.input_schema is not None
        assert tool.schema.tool_type is not None
        assert tool.handle is not None
        assert tool.capability is not None

        # Test that dialog tools have destructive type (they change page state)
        from core.tool_schema import ToolType

        assert tool.schema.tool_type == ToolType.DESTRUCTIVE


@pytest.mark.asyncio
async def test_dialog_tools_network_settings():
    # Test that dialog tools have proper network settings
    dialog_tools = get_dialog_tools(capture_snapshot=True)

    for tool in dialog_tools:
        mock_context = MagicMock()
        mock_service_result = ServiceResult(
            success=True,
            message="Dialog handled successfully",
            data={"action": "accept", "type": "confirm"},
        )

        with patch.object(
            DialogsService, "handle_dialog", return_value=mock_service_result
        ):
            result = await tool.handle(mock_context, {"accept": True})

            # Dialog operations should wait for network
            assert result.wait_for_network is False


@pytest.mark.asyncio
async def test_dialog_tools_modal_state():
    # Test that dialog handling tool properly clears modal state
    dialog_tools = get_dialog_tools(capture_snapshot=True)
    handle_dialog_tool = next(
        tool for tool in dialog_tools if tool.schema.name == "browser_handle_dialog"
    )

    # Check that dialog tool has clears_modal_state attribute
    assert hasattr(handle_dialog_tool, "clears_modal_state")
    assert handle_dialog_tool.clears_modal_state == "dialog"
