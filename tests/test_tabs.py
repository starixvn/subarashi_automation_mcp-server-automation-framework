import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import sys
from pathlib import Path

# Add the parent directory to the path so we can import from the main package
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.conftest import assert_text_content, assert_contains_text_content
from context import ServerContext
from config.settings import Config, get_default_config, config_to_settings
from tools.tabs import get_tab_tools
from services.tabs_service import TabsService
from services.base_service import ServiceResult


@pytest.mark.asyncio
async def test_browser_tab_list():
    # Test tab listing functionality
    tab_tools = get_tab_tools(capture_snapshot=False)
    tab_list_tool = next(
        tool for tool in tab_tools if tool.schema.name == "browser_tab_list"
    )

    # Mock service result
    mock_service_result = {
        "success": True,
        "data": {
            "tabs": [
                {
                    "index": 0,
                    "title": "Example Domain",
                    "url": "https://example.com",
                    "is_current": True,
                },
                {
                    "index": 1,
                    "title": "Google",
                    "url": "https://google.com",
                    "is_current": False,
                },
            ],
            "count": 2,
        },
    }

    # Create mock context
    mock_context = MagicMock()

    with patch.object(TabsService, "list_tabs", return_value=mock_service_result):
        result = await tab_list_tool.handle(mock_context, {})

        # Test ToolResult structure
        assert result.code == ["# List browser tabs"]
        assert result.capture_snapshot is False
        assert result.wait_for_network is False
        assert result.action is not None

        # Test action execution
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert "Browser Tabs (2 total)" in action_result.content[0]["text"]
        assert "Example Domain" in action_result.content[0]["text"]


@pytest.mark.asyncio
async def test_browser_tab_new():
    # Test creating new tab with URL
    tab_tools = get_tab_tools(capture_snapshot=False)
    tab_new_tool = next(
        tool for tool in tab_tools if tool.schema.name == "browser_tab_new"
    )

    # Mock service result
    mock_service_result = {
        "success": True,
        "data": {
            "title": "Example Domain",
            "url": "https://example.com",
            "tab_count": 3,
        },
    }

    # Create mock context
    mock_context = MagicMock()

    with patch.object(TabsService, "create_new_tab", return_value=mock_service_result):
        result = await tab_new_tool.handle(mock_context, {"url": "https://example.com"})

        # Test ToolResult structure
        assert result.code == ["# Open new tab"]
        assert result.capture_snapshot is False
        assert result.wait_for_network is False
        assert result.action is not None

        # Test action execution
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert "Created new tab: Example Domain" in action_result.content[0]["text"]
        assert "https://example.com" in action_result.content[0]["text"]


@pytest.mark.asyncio
async def test_browser_tab_new_no_url():
    # Test creating new tab without URL
    tab_tools = get_tab_tools(capture_snapshot=False)
    tab_new_tool = next(
        tool for tool in tab_tools if tool.schema.name == "browser_tab_new"
    )

    # Mock service result
    mock_service_result = {
        "success": True,
        "data": {"title": "New Tab", "url": "about:blank", "tab_count": 2},
    }

    # Create mock context
    mock_context = MagicMock()

    with patch.object(TabsService, "create_new_tab", return_value=mock_service_result):
        result = await tab_new_tool.handle(mock_context, {})

        # Test ToolResult structure
        assert result.code == ["# Open new tab"]
        assert result.capture_snapshot is False
        assert result.wait_for_network is False
        assert result.action is not None

        # Test action execution
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert "Created new tab: New Tab" in action_result.content[0]["text"]


@pytest.mark.asyncio
async def test_browser_tab_select():
    # Test selecting tab by index
    tab_tools = get_tab_tools(capture_snapshot=False)
    tab_select_tool = next(
        tool for tool in tab_tools if tool.schema.name == "browser_tab_select"
    )

    # Mock service result
    mock_service_result = {
        "success": True,
        "data": {"index": 1, "title": "Google", "url": "https://google.com"},
    }

    # Create mock context
    mock_context = MagicMock()

    with patch.object(TabsService, "select_tab", return_value=mock_service_result):
        result = await tab_select_tool.handle(mock_context, {"index": 1})

        # Test ToolResult structure
        assert result.code == ["# Select tab 1"]
        assert result.capture_snapshot is False
        assert result.wait_for_network is False
        assert result.action is not None

        # Test action execution
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert "Selected tab 1: Google" in action_result.content[0]["text"]


@pytest.mark.asyncio
async def test_browser_tab_close():
    # Test closing tab by index
    tab_tools = get_tab_tools(capture_snapshot=False)
    tab_close_tool = next(
        tool for tool in tab_tools if tool.schema.name == "browser_tab_close"
    )

    # Mock service result
    mock_service_result = {
        "success": True,
        "data": {"closed_index": 1, "remaining_tabs": 2},
    }

    # Create mock context
    mock_context = MagicMock()

    with patch.object(TabsService, "close_tab", return_value=mock_service_result):
        result = await tab_close_tool.handle(mock_context, {"index": 1})

        # Test ToolResult structure
        assert result.code == ["# Close tab 1"]
        assert result.capture_snapshot is False
        assert result.wait_for_network is False
        assert result.action is not None

        # Test action execution
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert "Closed tab 1" in action_result.content[0]["text"]


@pytest.mark.asyncio
async def test_browser_tab_close_current():
    # Test closing current tab
    tab_tools = get_tab_tools(capture_snapshot=False)
    tab_close_tool = next(
        tool for tool in tab_tools if tool.schema.name == "browser_tab_close"
    )

    # Mock service result
    mock_service_result = {
        "success": True,
        "data": {"closed_index": 0, "remaining_tabs": 1},
    }

    # Create mock context
    mock_context = MagicMock()

    with patch.object(TabsService, "close_tab", return_value=mock_service_result):
        result = await tab_close_tool.handle(mock_context, {})

        # Test action execution
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert "Closed tab 0" in action_result.content[0]["text"]


@pytest.mark.asyncio
async def test_browser_tab_list_error():
    # Test error handling in tab listing
    tab_tools = get_tab_tools(capture_snapshot=False)
    tab_list_tool = next(
        tool for tool in tab_tools if tool.schema.name == "browser_tab_list"
    )

    # Mock service error result
    mock_service_result = {"success": False, "error": "No browser context available"}

    # Create mock context
    mock_context = MagicMock()

    with patch.object(TabsService, "list_tabs", return_value=mock_service_result):
        result = await tab_list_tool.handle(mock_context, {})

        # Test action execution with error
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert (
            "Error listing tabs: No browser context available"
            in action_result.content[0]["text"]
        )


@pytest.mark.asyncio
async def test_browser_tab_select_error():
    # Test error handling in tab selection
    tab_tools = get_tab_tools(capture_snapshot=False)
    tab_select_tool = next(
        tool for tool in tab_tools if tool.schema.name == "browser_tab_select"
    )

    # Mock service error result
    mock_service_result = {"success": False, "error": "Tab index out of range"}

    # Create mock context
    mock_context = MagicMock()

    with patch.object(TabsService, "select_tab", return_value=mock_service_result):
        result = await tab_select_tool.handle(mock_context, {"index": 99})

        # Test action execution with error
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert (
            "Failed to select tab: Tab index out of range"
            in action_result.content[0]["text"]
        )


@pytest.mark.asyncio
async def test_tabs_capability_filtering():
    # Test that tab tools have proper capability filtering
    tab_tools = get_tab_tools(capture_snapshot=False)

    # Check that we have the expected tab tools
    tool_names = [tool.schema.name for tool in tab_tools]
    expected_tools = [
        "browser_tab_list",
        "browser_tab_new",
        "browser_tab_select",
        "browser_tab_close",
    ]

    for expected_tool in expected_tools:
        assert expected_tool in tool_names, f"Missing tab tool: {expected_tool}"

    # Check that all tools have TABS capability
    from core.tool_schema import ToolCapability

    for tool in tab_tools:
        assert tool.capability == ToolCapability.TABS


@pytest.mark.asyncio
async def test_tab_tools_capture_snapshot_parameter():
    # Test that tab tools respect capture_snapshot parameter
    tools_with_snapshot = get_tab_tools(capture_snapshot=True)
    tools_without_snapshot = get_tab_tools(capture_snapshot=False)

    # Find tab new tool in both sets
    tab_new_with_snapshot = next(
        tool for tool in tools_with_snapshot if tool.schema.name == "browser_tab_new"
    )
    tab_new_without_snapshot = next(
        tool for tool in tools_without_snapshot if tool.schema.name == "browser_tab_new"
    )

    # Create mock context and service result
    mock_context = MagicMock()
    mock_service_result = {
        "success": True,
        "data": {"title": "New Tab", "url": "about:blank", "tab_count": 2},
    }

    with patch.object(TabsService, "create_new_tab", return_value=mock_service_result):
        result_with_snapshot = await tab_new_with_snapshot.handle(mock_context, {})
        result_without_snapshot = await tab_new_without_snapshot.handle(
            mock_context, {}
        )

        assert result_with_snapshot.capture_snapshot is True
        assert result_without_snapshot.capture_snapshot is False


@pytest.mark.asyncio
async def test_tab_tools_schema_validation():
    # Test that tab tools have proper schema validation
    tab_tools = get_tab_tools(capture_snapshot=False)

    for tool in tab_tools:
        assert tool.schema.name is not None
        assert tool.schema.title is not None
        assert tool.schema.description is not None
        assert tool.schema.input_schema is not None
        assert tool.schema.tool_type is not None
        assert tool.handle is not None
        assert tool.capability is not None

        # Test that tab tools have correct types
        from core.tool_schema import ToolType

        if tool.schema.name == "browser_tab_close":
            assert tool.schema.tool_type == ToolType.DESTRUCTIVE
        else:
            assert tool.schema.tool_type == ToolType.READ_ONLY


@pytest.mark.asyncio
async def test_tab_tools_network_settings():
    # Test that tab tools have proper network settings
    tab_tools = get_tab_tools(capture_snapshot=False)

    for tool in tab_tools:
        mock_context = MagicMock()
        mock_service_result = {
            "success": True,
            "data": {"title": "Test", "url": "about:blank", "tab_count": 1},
        }

        with patch.object(TabsService, "list_tabs", return_value=mock_service_result):
            with patch.object(
                TabsService, "create_new_tab", return_value=mock_service_result
            ):
                with patch.object(
                    TabsService, "select_tab", return_value=mock_service_result
                ):
                    with patch.object(
                        TabsService, "close_tab", return_value=mock_service_result
                    ):
                        if tool.schema.name == "browser_tab_list":
                            result = await tool.handle(mock_context, {})
                        elif tool.schema.name == "browser_tab_new":
                            result = await tool.handle(mock_context, {})
                        elif tool.schema.name == "browser_tab_select":
                            result = await tool.handle(mock_context, {"index": 1})
                        elif tool.schema.name == "browser_tab_close":
                            result = await tool.handle(mock_context, {"index": 1})

                        # Tab operations shouldn't wait for network
                        assert result.wait_for_network is False
