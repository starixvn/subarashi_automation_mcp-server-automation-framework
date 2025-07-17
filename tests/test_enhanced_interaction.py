import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import sys
from pathlib import Path

# Add the parent directory to the path so we can import from the main package
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.conftest import assert_text_content, assert_contains_text_content
from context import ServerContext
from config.settings import Config, get_default_config, config_to_settings
from tools.interaction import get_interaction_tools
from services.interaction_service import InteractionService
from services.base_service import ServiceResult


@pytest.mark.asyncio
async def test_browser_click():
    # Test the browser_click tool with InteractionService
    interaction_tools = get_interaction_tools(capture_snapshot=True)
    click_tool = next(
        tool for tool in interaction_tools if tool.schema.name == "browser_click"
    )

    # Mock service result
    mock_service_result = ServiceResult(
        success=True,
        message="Successfully clicked on Submit button",
        data={"element": "Submit button", "ref": "e1"},
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(
        InteractionService, "click_element", return_value=mock_service_result
    ):
        result = await click_tool.handle(
            mock_context, {"element": "Submit button", "ref": "e1"}
        )

        # Test ToolResult structure
        assert result.code == [
            "# Click on Submit button",
            "# Using element reference: e1",
        ]
        assert result.capture_snapshot is True
        assert result.wait_for_network is True
        assert result.action is not None

        # Test action execution
        action_result = await result.action()
        assert len(action_result.content) == 0  # Success case returns empty content


@pytest.mark.asyncio
async def test_browser_click_error():
    # Test error handling in browser_click
    interaction_tools = get_interaction_tools(capture_snapshot=True)
    click_tool = next(
        tool for tool in interaction_tools if tool.schema.name == "browser_click"
    )

    # Mock service error result
    mock_service_result = ServiceResult(
        success=False,
        message="Element not found: missing-button",
        error="Element not found",
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(
        InteractionService, "click_element", return_value=mock_service_result
    ):
        result = await click_tool.handle(
            mock_context, {"element": "missing-button", "ref": "e1"}
        )

        # Test action execution with error
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert "Element not found: missing-button" in action_result.content[0]["text"]


@pytest.mark.asyncio
async def test_browser_type():
    # Test the browser_type tool with InteractionService
    interaction_tools = get_interaction_tools(capture_snapshot=True)
    type_tool = next(
        tool for tool in interaction_tools if tool.schema.name == "browser_type"
    )

    # Mock service result
    mock_service_result = ServiceResult(
        success=True,
        message="Successfully typed 'Hello World' into input field",
        data={"element": "input field", "text": "Hello World", "ref": "e2"},
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(
        InteractionService, "type_text", return_value=mock_service_result
    ):
        result = await type_tool.handle(
            mock_context,
            {
                "element": "input field",
                "ref": "e2",
                "text": "Hello World",
                "submit": False,
            },
        )

        # Test ToolResult structure
        assert result.code == ["# Type text into input field", "# Text: 'Hello World'"]
        assert result.capture_snapshot is True
        assert result.wait_for_network is True
        assert result.action is not None

        # Test action execution
        action_result = await result.action()
        assert len(action_result.content) == 0  # Success case returns empty content


@pytest.mark.asyncio
async def test_browser_type_with_submit():
    # Test browser_type with submit=True
    interaction_tools = get_interaction_tools(capture_snapshot=True)
    type_tool = next(
        tool for tool in interaction_tools if tool.schema.name == "browser_type"
    )

    # Mock service result
    mock_service_result = ServiceResult(
        success=True,
        message="Successfully typed 'search query' and submitted",
        data={"element": "search box", "text": "search query", "ref": "e3"},
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(
        InteractionService, "type_text", return_value=mock_service_result
    ):
        result = await type_tool.handle(
            mock_context,
            {
                "element": "search box",
                "ref": "e3",
                "text": "search query",
                "submit": True,
            },
        )

        # Test ToolResult structure for type with submit
        assert result.code == [
            "# Type text into search box",
            "# Text: 'search query'",
            "# Submit after typing (press Enter)",
        ]

        # Test action execution
        action_result = await result.action()
        assert len(action_result.content) == 0  # Success case returns empty content


@pytest.mark.asyncio
async def test_browser_hover():
    # Test the browser_hover tool with InteractionService
    interaction_tools = get_interaction_tools(capture_snapshot=True)
    hover_tool = next(
        tool for tool in interaction_tools if tool.schema.name == "browser_hover"
    )

    # Mock service result
    mock_service_result = ServiceResult(
        success=True,
        message="Successfully hovered over dropdown menu",
        data={"element": "dropdown menu", "ref": "e4"},
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(
        InteractionService, "hover_element", return_value=mock_service_result
    ):
        result = await hover_tool.handle(
            mock_context, {"element": "dropdown menu", "ref": "e4"}
        )

        # Test ToolResult structure for hover
        assert result.code == [
            "# Hover over dropdown menu",
            "# Using element reference: e4",
        ]
        assert result.capture_snapshot is True
        assert result.wait_for_network is True
        assert result.action is not None

        # Test action execution - hover returns success message
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert (
            "Successfully hovered over dropdown menu"
            in action_result.content[0]["text"]
        )


@pytest.mark.asyncio
async def test_browser_select_option():
    # Test the browser_select_option tool with InteractionService
    interaction_tools = get_interaction_tools(capture_snapshot=True)
    select_tool = next(
        tool
        for tool in interaction_tools
        if tool.schema.name == "browser_select_option"
    )

    # Mock service result
    mock_service_result = ServiceResult(
        success=True,
        message="Successfully selected options: ['option1', 'option2']",
        data={
            "element": "select dropdown",
            "values": ["option1", "option2"],
            "ref": "e5",
        },
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(
        InteractionService, "select_option", return_value=mock_service_result
    ):
        result = await select_tool.handle(
            mock_context,
            {
                "element": "select dropdown",
                "ref": "e5",
                "values": ["option1", "option2"],
            },
        )

        # Test ToolResult structure for select option
        assert result.code == [
            "# Select options in select dropdown",
            "# Values: ['option1', 'option2']",
        ]
        assert result.capture_snapshot is True
        assert result.wait_for_network is True
        assert result.action is not None

        # Test action execution - select returns success message
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert (
            "Successfully selected options: ['option1', 'option2']"
            in action_result.content[0]["text"]
        )


@pytest.mark.asyncio
async def test_browser_get_text():
    # Test getting text content from element
    interaction_tools = get_interaction_tools(capture_snapshot=False)
    get_text_tool = next(
        tool for tool in interaction_tools if tool.schema.name == "browser_get_text"
    )

    # Mock service result
    mock_service_result = ServiceResult(
        success=True,
        message="Retrieved text content from #username",
        data={"selector": "#username", "text": "john_doe"},
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(
        InteractionService, "get_text_content", return_value=mock_service_result
    ):
        result = await get_text_tool.handle(mock_context, {"selector": "#username"})

        # Test ToolResult structure for get text
        assert result.code == [
            "# Get text content from element",
            "# Selector: '#username'",
        ]
        assert result.capture_snapshot is False
        assert result.wait_for_network is False
        assert result.action is not None

        # Test action execution - get text returns formatted content
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        content_text = action_result.content[0]["text"]
        assert "Text content:" in content_text
        assert "john_doe" in content_text


@pytest.mark.asyncio
async def test_browser_get_text_error():
    # Test error handling in get text
    interaction_tools = get_interaction_tools(capture_snapshot=False)
    get_text_tool = next(
        tool for tool in interaction_tools if tool.schema.name == "browser_get_text"
    )

    # Mock service error result
    mock_service_result = ServiceResult(
        success=False,
        message="Failed to get text from #missing: Element not found",
        error="Element not found",
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(
        InteractionService, "get_text_content", return_value=mock_service_result
    ):
        result = await get_text_tool.handle(mock_context, {"selector": "#missing"})

        # Test action execution with error
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert (
            "Failed to get text from #missing: Element not found"
            in action_result.content[0]["text"]
        )


@pytest.mark.asyncio
async def test_browser_drag():
    # Test the browser_drag tool with InteractionService
    interaction_tools = get_interaction_tools(capture_snapshot=True)
    drag_tool = next(
        tool for tool in interaction_tools if tool.schema.name == "browser_drag"
    )

    # Mock service result
    mock_service_result = ServiceResult(
        success=True,
        message="Successfully dragged element from source to target",
        data={
            "start_element": "draggable item",
            "end_element": "drop zone",
            "start_ref": "e6",
            "end_ref": "e7",
        },
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(
        InteractionService, "drag_element", return_value=mock_service_result
    ):
        result = await drag_tool.handle(
            mock_context,
            {
                "start_element": "draggable item",
                "start_ref": "e6",
                "end_element": "drop zone",
                "end_ref": "e7",
            },
        )

        # Test ToolResult structure for drag
        assert result.code == [
            "# Drag element from draggable item to drop zone",
            "# Start ref: e6",
            "# End ref: e7",
        ]
        assert result.capture_snapshot is True
        assert result.wait_for_network is True
        assert result.action is not None

        # Test action execution - drag returns success message
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert (
            "Successfully dragged element from source to target"
            in action_result.content[0]["text"]
        )


@pytest.mark.asyncio
async def test_browser_drag_error():
    # Test error handling in browser_drag
    interaction_tools = get_interaction_tools(capture_snapshot=True)
    drag_tool = next(
        tool for tool in interaction_tools if tool.schema.name == "browser_drag"
    )

    # Mock service error result
    mock_service_result = ServiceResult(
        success=False,
        message="Source element not found: .missing",
        error="Source element not found",
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(
        InteractionService, "drag_element", return_value=mock_service_result
    ):
        result = await drag_tool.handle(
            mock_context,
            {
                "start_element": "missing element",
                "start_ref": "e6",
                "end_element": "target",
                "end_ref": "e7",
            },
        )

        # Test action execution with error
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert "Source element not found: .missing" in action_result.content[0]["text"]


@pytest.mark.asyncio
async def test_interaction_tools_capability_filtering():
    # Test that interaction tools have proper capability filtering
    interaction_tools = get_interaction_tools(capture_snapshot=True)

    # Check that we have the expected interaction tools
    tool_names = [tool.schema.name for tool in interaction_tools]
    expected_tools = [
        "browser_click",
        "browser_type",
        "browser_hover",
        "browser_select_option",
        "browser_get_text",
        "browser_drag",
    ]

    for expected_tool in expected_tools:
        assert expected_tool in tool_names, f"Missing interaction tool: {expected_tool}"

    # Check that all tools have CORE capability (interaction tools are core)
    from core.tool_schema import ToolCapability

    for tool in interaction_tools:
        assert tool.capability == ToolCapability.CORE


@pytest.mark.asyncio
async def test_interaction_tools_capture_snapshot_parameter():
    # Test that interaction tools respect capture_snapshot parameter
    tools_with_snapshot = get_interaction_tools(capture_snapshot=True)
    tools_without_snapshot = get_interaction_tools(capture_snapshot=False)

    # Find click tool in both sets
    click_with_snapshot = next(
        tool for tool in tools_with_snapshot if tool.schema.name == "browser_click"
    )
    click_without_snapshot = next(
        tool for tool in tools_without_snapshot if tool.schema.name == "browser_click"
    )

    # Create mock context and service result
    mock_context = MagicMock()
    mock_service_result = ServiceResult(
        success=True,
        message="Successfully clicked element",
        data={"element": "button", "ref": "e1"},
    )

    with patch.object(
        InteractionService, "click_element", return_value=mock_service_result
    ):
        result_with_snapshot = await click_with_snapshot.handle(
            mock_context, {"element": "button", "ref": "e1"}
        )
        result_without_snapshot = await click_without_snapshot.handle(
            mock_context, {"element": "button", "ref": "e1"}
        )

        assert result_with_snapshot.capture_snapshot is True
        assert result_without_snapshot.capture_snapshot is False


@pytest.mark.asyncio
async def test_interaction_tools_schema_validation():
    # Test that interaction tools have proper schema validation
    interaction_tools = get_interaction_tools(capture_snapshot=True)

    for tool in interaction_tools:
        assert tool.schema.name is not None
        assert tool.schema.title is not None
        assert tool.schema.description is not None
        assert tool.schema.input_schema is not None
        assert tool.schema.tool_type is not None
        assert tool.handle is not None
        assert tool.capability is not None

        # Test that tools have proper destructive type (they change page state)
        from core.tool_schema import ToolType

        if tool.schema.name in [
            "browser_get_text",
            "browser_hover",
        ]:  # these are read-only
            assert tool.schema.tool_type == ToolType.READ_ONLY
        else:
            assert tool.schema.tool_type == ToolType.DESTRUCTIVE
