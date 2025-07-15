import pytest
import tempfile
import base64
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock

from tests.conftest import assert_text_content, assert_contains_text_content
from context import ServerContext
from config.settings import Config, get_default_config, config_to_settings
from tools.vision import get_vision_tools, get_screenshot_tools
from services.vision_service import VisionService
from services.base_service import ServiceResult


@pytest.mark.asyncio
async def test_browser_screenshot():
    # Test basic screenshot functionality
    vision_tools = get_vision_tools(capture_snapshot=False)
    screenshot_tool = next(
        tool for tool in vision_tools if tool.schema.name == "browser_screenshot"
    )

    # Mock service result with bytes data
    mock_service_result = ServiceResult(
        success=True,
        message="Screenshot taken of https://example.com",
        data={
            "url": "https://example.com",
            "full_page": False,
            "has_screenshot": True,
            "content": [
                {
                    "type": "screenshot",
                    "data": b"fake_image_data",  # Raw bytes data
                    "url": "https://example.com",
                }
            ],
        },
    )

    # Create mock context
    mock_context = MagicMock()
    mock_context.client_supports_images.return_value = True

    with patch.object(
        VisionService, "take_screenshot", return_value=mock_service_result
    ):
        result = await screenshot_tool.handle(mock_context, {"full_page": False})

        # Test ToolResult structure - updated for enhanced version
        assert result.code == [
            "# Take enhanced screenshot with advanced options",
            "# Full page: False",
            "# Format: png",
            "# Quality: 80",
        ]
        assert result.capture_snapshot is False
        assert result.wait_for_network is False
        assert result.action is not None

        # Test action execution
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert (
            "Screenshot taken of https://example.com"
            in action_result.content[0]["text"]
        )


@pytest.mark.asyncio
async def test_browser_screenshot_full_page():
    # Test full page screenshot
    vision_tools = get_vision_tools(capture_snapshot=False)
    screenshot_tool = next(
        tool for tool in vision_tools if tool.schema.name == "browser_screenshot"
    )

    # Mock service result with bytes data
    mock_service_result = ServiceResult(
        success=True,
        message="Screenshot taken of https://example.com",
        data={
            "url": "https://example.com",
            "full_page": True,
            "has_screenshot": True,
            "content": [
                {
                    "type": "screenshot",
                    "data": b"fake_fullpage_image_data",  # Raw bytes data
                    "url": "https://example.com",
                }
            ],
        },
    )

    # Create mock context
    mock_context = MagicMock()
    mock_context.client_supports_images.return_value = True

    with patch.object(
        VisionService, "take_screenshot", return_value=mock_service_result
    ):
        result = await screenshot_tool.handle(mock_context, {"full_page": True})

        # Test ToolResult structure - updated for enhanced version
        assert result.code == [
            "# Take enhanced screenshot with advanced options",
            "# Full page: True",
            "# Format: png",
            "# Quality: 80",
        ]
        assert result.capture_snapshot is False
        assert result.wait_for_network is False
        assert result.action is not None

        # Test action execution
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert (
            "Screenshot taken of https://example.com"
            in action_result.content[0]["text"]
        )


@pytest.mark.asyncio
async def test_browser_save_screenshot():
    # Test saving screenshot to file
    vision_tools = get_vision_tools(capture_snapshot=False)
    save_screenshot_tool = next(
        tool for tool in vision_tools if tool.schema.name == "browser_save_screenshot"
    )

    # Mock service result
    mock_service_result = ServiceResult(
        success=True,
        message="Screenshot saved to /tmp/test_screenshot.png",
        data={
            "filename": "test_screenshot.png",
            "output_path": "/tmp/test_screenshot.png",
            "full_page": False,
        },
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(
        VisionService, "save_screenshot", return_value=mock_service_result
    ):
        result = await save_screenshot_tool.handle(
            mock_context, {"filename": "test_screenshot.png", "full_page": False}
        )

        # Test ToolResult structure - updated for enhanced version
        assert result.code == [
            "# Save enhanced screenshot to file",
            "# Filename: test_screenshot.png",
            "# Full page: False",
            "# Format: png",
            "# Quality: 80",
        ]
        assert result.capture_snapshot is False
        assert result.wait_for_network is False
        assert result.action is not None

        # Test action execution
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert (
            "Screenshot saved to /tmp/test_screenshot.png"
            in action_result.content[0]["text"]
        )


@pytest.mark.asyncio
async def test_browser_screen_click():
    # Test screen clicking
    vision_tools = get_vision_tools(capture_snapshot=True)
    screen_click_tool = next(
        tool for tool in vision_tools if tool.schema.name == "browser_screen_click"
    )

    # Mock service result
    mock_service_result = ServiceResult(
        success=True,
        message="Clicked at coordinates (100, 200)",
        data={"x": 100, "y": 200, "element": "button"},
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(VisionService, "screen_click", return_value=mock_service_result):
        result = await screen_click_tool.handle(
            mock_context, {"x": 100, "y": 200, "element": "button"}
        )

        # Test ToolResult structure - updated for enhanced version
        assert result.code == [
            "# Advanced screen click with validation",
            "# Position: (100, 200)",
            "# Element: button",
            "# Click type: left",
            "# Modifiers: []",
            "# Validate bounds: True",
        ]
        assert result.capture_snapshot is True
        assert result.wait_for_network is True  # Screen click waits for network
        assert result.action is not None

        # Test action execution
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert "Clicked at coordinates (100, 200)" in action_result.content[0]["text"]


@pytest.mark.asyncio
async def test_browser_capture_snapshot():
    # Test capturing page snapshot
    vision_tools = get_vision_tools(capture_snapshot=False)
    capture_snapshot_tool = next(
        tool for tool in vision_tools if tool.schema.name == "browser_capture_snapshot"
    )

    # Mock service result
    mock_service_result = ServiceResult(
        success=True,
        message="Page snapshot captured",
        data={
            "url": "https://example.com",
            "text": "Example Domain\nThis domain is for use in illustrative examples in documents.",
            "has_screenshot": True,
            "include_screenshot": True,
        },
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(
        VisionService, "capture_snapshot", return_value=mock_service_result
    ):
        result = await capture_snapshot_tool.handle(mock_context, {})

        # Test ToolResult structure - updated for enhanced version
        assert result.code == [
            "# Capture enhanced page snapshot",
            "# Includes accessibility tree, page content, and element references",
        ]
        assert result.capture_snapshot is False
        assert result.wait_for_network is False
        assert result.action is not None

        # Test action execution
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"


@pytest.mark.asyncio
async def test_browser_screenshot_error():
    # Test error handling in screenshot
    vision_tools = get_vision_tools(capture_snapshot=False)
    screenshot_tool = next(
        tool for tool in vision_tools if tool.schema.name == "browser_screenshot"
    )

    # Mock service error result
    mock_service_result = ServiceResult(
        success=False,
        message="Failed to take screenshot: No page available",
        error="No page available",
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(
        VisionService, "take_screenshot", return_value=mock_service_result
    ):
        result = await screenshot_tool.handle(mock_context, {"full_page": False})

        # Test action execution with error
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert (
            "Failed to take screenshot: No page available"
            in action_result.content[0]["text"]
        )


@pytest.mark.asyncio
async def test_browser_save_screenshot_error():
    # Test error handling in save screenshot
    vision_tools = get_vision_tools(capture_snapshot=False)
    save_screenshot_tool = next(
        tool for tool in vision_tools if tool.schema.name == "browser_save_screenshot"
    )

    # Mock service error result
    mock_service_result = ServiceResult(
        success=False,
        message="Failed to save screenshot: Could not save screenshot file",
        error="Could not save screenshot file",
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(
        VisionService, "save_screenshot", return_value=mock_service_result
    ):
        result = await save_screenshot_tool.handle(
            mock_context, {"filename": "test_screenshot.png", "full_page": False}
        )

        # Test action execution with error
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert (
            "Failed to save screenshot: Could not save screenshot file"
            in action_result.content[0]["text"]
        )


@pytest.mark.asyncio
async def test_vision_capability_filtering():
    # Test that vision tools have proper capability filtering
    vision_tools = get_vision_tools(capture_snapshot=False)

    # Check that we have the expected vision tools
    tool_names = [tool.schema.name for tool in vision_tools]
    expected_tools = [
        "browser_screenshot",
        "browser_save_screenshot",
        "browser_screen_click",
        "browser_screen_drag",
        "browser_screen_type",
        "browser_move_mouse",
        "browser_capture_snapshot",
    ]

    for expected_tool in expected_tools:
        assert expected_tool in tool_names, f"Missing vision tool: {expected_tool}"

    # Check that all tools have VISION capability
    from core.tool_schema import ToolCapability

    for tool in vision_tools:
        assert tool.capability == ToolCapability.VISION


@pytest.mark.asyncio
async def test_screenshot_tools_filtering():
    # Test screenshot-only tools
    screenshot_tools = get_screenshot_tools(capture_snapshot=False)

    # Check that we have the expected screenshot tools
    tool_names = [tool.schema.name for tool in screenshot_tools]
    expected_tools = ["browser_screenshot", "browser_save_screenshot"]

    for expected_tool in expected_tools:
        assert expected_tool in tool_names, f"Missing screenshot tool: {expected_tool}"

    # Check that all tools have VISION capability
    from core.tool_schema import ToolCapability

    for tool in screenshot_tools:
        assert tool.capability == ToolCapability.VISION


@pytest.mark.asyncio
async def test_vision_tools_capture_snapshot_parameter():
    # Test that vision tools respect capture_snapshot parameter
    tools_with_snapshot = get_vision_tools(capture_snapshot=True)
    tools_without_snapshot = get_vision_tools(capture_snapshot=False)

    # Find screen click tool in both sets
    screen_click_with_snapshot = next(
        tool
        for tool in tools_with_snapshot
        if tool.schema.name == "browser_screen_click"
    )
    screen_click_without_snapshot = next(
        tool
        for tool in tools_without_snapshot
        if tool.schema.name == "browser_screen_click"
    )

    # Create mock context and service result
    mock_context = MagicMock()
    mock_service_result = ServiceResult(
        success=True,
        message="Clicked at coordinates (100, 100)",
        data={"x": 100, "y": 100, "element": "button"},
    )

    with patch.object(VisionService, "screen_click", return_value=mock_service_result):
        result_with_snapshot = await screen_click_with_snapshot.handle(
            mock_context, {"x": 100, "y": 100, "element": "button"}
        )
        result_without_snapshot = await screen_click_without_snapshot.handle(
            mock_context, {"x": 100, "y": 100, "element": "button"}
        )

        assert result_with_snapshot.capture_snapshot is True
        assert result_without_snapshot.capture_snapshot is False


@pytest.mark.asyncio
async def test_vision_tools_schema_validation():
    # Test that vision tools have proper schema validation
    vision_tools = get_vision_tools(capture_snapshot=False)

    for tool in vision_tools:
        assert tool.schema.name is not None
        assert tool.schema.title is not None
        assert tool.schema.description is not None
        assert tool.schema.input_schema is not None
        assert tool.schema.tool_type is not None
        assert tool.handle is not None
        assert tool.capability is not None

        # Test that vision tools have appropriate types
        from core.tool_schema import ToolType

        if tool.schema.name in [
            "browser_screenshot",
            "browser_save_screenshot",
            "browser_capture_snapshot",
        ]:
            assert tool.schema.tool_type == ToolType.READ_ONLY
        else:  # Interactive tools like click, drag, type, move
            assert tool.schema.tool_type == ToolType.DESTRUCTIVE


@pytest.mark.asyncio
async def test_vision_tools_network_settings():
    # Test that vision tools have proper network settings
    vision_tools = get_vision_tools(capture_snapshot=False)

    for tool in vision_tools:
        mock_context = MagicMock()
        mock_service_result = ServiceResult(
            success=True, message="Operation successful", data={}
        )

        with patch.object(
            VisionService, "take_screenshot", return_value=mock_service_result
        ):
            with patch.object(
                VisionService, "save_screenshot", return_value=mock_service_result
            ):
                with patch.object(
                    VisionService, "screen_click", return_value=mock_service_result
                ):
                    with patch.object(
                        VisionService, "screen_drag", return_value=mock_service_result
                    ):
                        with patch.object(
                            VisionService,
                            "screen_type",
                            return_value=mock_service_result,
                        ):
                            with patch.object(
                                VisionService,
                                "move_mouse",
                                return_value=mock_service_result,
                            ):
                                with patch.object(
                                    VisionService,
                                    "capture_snapshot",
                                    return_value=mock_service_result,
                                ):
                                    if tool.schema.name == "browser_screenshot":
                                        result = await tool.handle(
                                            mock_context, {"full_page": False}
                                        )
                                        assert result.wait_for_network is False
                                    elif tool.schema.name == "browser_save_screenshot":
                                        result = await tool.handle(
                                            mock_context,
                                            {
                                                "filename": "test.png",
                                                "full_page": False,
                                            },
                                        )
                                        assert result.wait_for_network is False
                                    elif tool.schema.name == "browser_screen_click":
                                        result = await tool.handle(
                                            mock_context,
                                            {"x": 100, "y": 100, "element": "button"},
                                        )
                                        # Screen click waits for network in enhanced version
                                        assert result.wait_for_network is True
                                    elif tool.schema.name == "browser_screen_drag":
                                        result = await tool.handle(
                                            mock_context,
                                            {
                                                "element": "button",
                                                "from_x": 100,
                                                "from_y": 100,
                                                "to_x": 200,
                                                "to_y": 200,
                                            },
                                        )
                                        assert result.wait_for_network is True
                                    elif tool.schema.name == "browser_screen_type":
                                        result = await tool.handle(
                                            mock_context,
                                            {
                                                "text": "test",
                                                "element": "input",
                                                "x": 100,
                                                "y": 100,
                                            },
                                        )
                                        assert result.wait_for_network is True
                                    elif tool.schema.name == "browser_move_mouse":
                                        result = await tool.handle(
                                            mock_context,
                                            {"element": "button", "x": 100, "y": 100},
                                        )
                                        assert result.wait_for_network is False
                                    elif tool.schema.name == "browser_capture_snapshot":
                                        result = await tool.handle(mock_context, {})
                                        assert result.wait_for_network is False
