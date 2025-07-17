import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from pathlib import Path

from tools.vision import (
    get_vision_tools,
    get_screenshot_tools,
    get_vision_screen_tools,
    browser_screenshot_factory,
    browser_save_screenshot_factory,
    browser_screen_click_factory,
    browser_screen_drag_factory,
    browser_screen_type_factory,
    browser_move_mouse_factory,
    browser_capture_snapshot_factory,
)
from services.vision_service import VisionService
from services.base_service import ServiceResult
from core.schemas import ScreenshotInputSchema, SaveScreenshotInputSchema


class TestEnhancedVisionService:
    """Test enhanced vision service functionality."""

    @pytest.fixture
    def mock_context(self):
        context = Mock()
        context.current_tab_or_die.return_value = Mock()
        context.client_supports_images.return_value = True
        context.settings.output_dir = Path("/tmp/test_screenshots")
        return context

    @pytest.fixture
    def vision_service(self, mock_context):
        return VisionService(mock_context)

    @pytest.mark.asyncio
    async def test_take_screenshot_success(self, vision_service):
        """Test successful screenshot with advanced options."""
        # Mock tab and page
        mock_tab = vision_service.context.current_tab_or_die.return_value
        mock_page = Mock()
        mock_tab.page = mock_page
        mock_page.url = "https://example.com"
        mock_page.screenshot = AsyncMock(return_value=b"fake_screenshot_data")

        result = await vision_service.take_screenshot(
            full_page=True,
            quality=90,
            format="jpeg",
            element_selector=None,
            clip_region=None,
        )

        assert result.success
        assert "Screenshot taken of https://example.com" in result.message
        assert result.data["format"] == "jpeg"
        assert result.data["quality"] == 90
        assert result.data["has_screenshot"] == True
        assert result.data["size_bytes"] == len(b"fake_screenshot_data")

        # Verify screenshot was called with correct options
        mock_page.screenshot.assert_called_once()
        call_args = mock_page.screenshot.call_args[1]
        assert call_args["full_page"] == True
        assert call_args["type"] == "jpeg"
        assert call_args["quality"] == 90

    @pytest.mark.asyncio
    async def test_take_screenshot_element_selector(self, vision_service):
        """Test screenshot with element selector."""
        mock_tab = vision_service.context.current_tab_or_die.return_value
        mock_page = Mock()
        mock_tab.page = mock_page
        mock_page.url = "https://example.com"

        # Mock element
        mock_element = Mock()
        mock_element.screenshot = AsyncMock(return_value=b"element_screenshot")
        mock_page.wait_for_selector = AsyncMock(return_value=mock_element)

        result = await vision_service.take_screenshot(element_selector="#test-element")

        assert result.success
        assert "element: #test-element" in result.message
        mock_page.wait_for_selector.assert_called_once_with(
            "#test-element", timeout=5000, state="visible"
        )
        mock_element.screenshot.assert_called_once()

    @pytest.mark.asyncio
    async def test_take_screenshot_clip_region(self, vision_service):
        """Test screenshot with clip region."""
        mock_tab = vision_service.context.current_tab_or_die.return_value
        mock_page = Mock()
        mock_tab.page = mock_page
        mock_page.url = "https://example.com"
        mock_page.screenshot = AsyncMock(return_value=b"clipped_screenshot")
        mock_page.evaluate = AsyncMock(return_value={"width": 1920, "height": 1080})

        clip_region = {"x": 100, "y": 100, "width": 800, "height": 600}

        result = await vision_service.take_screenshot(clip_region=clip_region)

        assert result.success
        assert "region: 800x600" in result.message

        call_args = mock_page.screenshot.call_args[1]
        assert call_args["clip"] == clip_region

    @pytest.mark.asyncio
    async def test_take_screenshot_invalid_format(self, vision_service):
        """Test screenshot with invalid format."""
        result = await vision_service.take_screenshot(format="invalid")

        assert not result.success
        assert "Invalid format 'invalid'" in result.message

    @pytest.mark.asyncio
    async def test_take_screenshot_invalid_quality(self, vision_service):
        """Test screenshot with invalid quality."""
        result = await vision_service.take_screenshot(format="jpeg", quality=150)

        assert not result.success
        assert "Invalid quality '150'" in result.message

    @pytest.mark.asyncio
    async def test_screen_click_with_validation(self, vision_service):
        """Test screen click with coordinate validation."""
        mock_tab = vision_service.context.current_tab_or_die.return_value
        mock_page = Mock()
        mock_tab.page = mock_page
        mock_page.evaluate = AsyncMock(return_value={"width": 1920, "height": 1080})
        mock_page.mouse.click = AsyncMock()
        mock_page.keyboard.down = AsyncMock()
        mock_page.keyboard.up = AsyncMock()

        result = await vision_service.screen_click(
            x=500,
            y=300,
            element="Test Button",
            click_type="left",
            modifiers=["Control"],
            validate_bounds=True,
        )

        assert result.success
        assert "Clicked at coordinates (500, 300)" in result.message
        assert "Test Button" in result.message
        assert result.data["coordinates_validated"] == True

        mock_page.keyboard.down.assert_called_once_with("Control")
        mock_page.mouse.click.assert_called_once()
        mock_page.keyboard.up.assert_called_once_with("Control")

    @pytest.mark.asyncio
    async def test_screen_click_invalid_coordinates(self, vision_service):
        """Test screen click with invalid coordinates."""
        mock_tab = vision_service.context.current_tab_or_die.return_value
        mock_page = Mock()
        mock_tab.page = mock_page
        mock_page.evaluate = AsyncMock(return_value={"width": 1920, "height": 1080})

        result = await vision_service.screen_click(
            x=2000,  # Outside viewport
            y=300,
            validate_bounds=True,
        )

        assert not result.success
        assert "Invalid coordinates" in result.message

    @pytest.mark.asyncio
    async def test_screen_drag_smooth_movement(self, vision_service):
        """Test screen drag with smooth movement."""
        mock_tab = vision_service.context.current_tab_or_die.return_value
        mock_page = Mock()
        mock_tab.page = mock_page
        mock_page.evaluate = AsyncMock(return_value={"width": 1920, "height": 1080})
        mock_page.mouse.move = AsyncMock()
        mock_page.mouse.down = AsyncMock()
        mock_page.mouse.up = AsyncMock()

        result = await vision_service.screen_drag(
            from_x=100, from_y=100, to_x=200, to_y=200, element="Drag Element", steps=5
        )

        assert result.success
        assert "Dragged from (100, 100) to (200, 200)" in result.message
        assert result.data["steps"] == 5

        # Should call mouse.move multiple times for smooth movement
        assert mock_page.mouse.move.call_count > 5
        mock_page.mouse.down.assert_called_once()
        mock_page.mouse.up.assert_called_once()

    @pytest.mark.asyncio
    async def test_screen_type_with_clear(self, vision_service):
        """Test screen type with clear first option."""
        mock_tab = vision_service.context.current_tab_or_die.return_value
        mock_page = Mock()
        mock_tab.page = mock_page
        mock_page.evaluate = AsyncMock(return_value={"width": 1920, "height": 1080})
        mock_page.mouse.click = AsyncMock()
        mock_page.keyboard.press = AsyncMock()
        mock_page.keyboard.type = AsyncMock()

        result = await vision_service.screen_type(
            x=300, y=400, text="Hello World", clear_first=True, delay=50
        )

        assert result.success
        assert "Typed text at (300, 400): 'Hello World'" in result.message
        assert result.data["text_length"] == 11
        assert result.data["clear_first"] == True

        mock_page.mouse.click.assert_called_once_with(300, 400)
        mock_page.keyboard.press.assert_called_once_with("Control+a")
        mock_page.keyboard.type.assert_called_once_with("Hello World", delay=50)

    @pytest.mark.asyncio
    async def test_move_mouse_smooth(self, vision_service):
        """Test smooth mouse movement."""
        mock_tab = vision_service.context.current_tab_or_die.return_value
        mock_page = Mock()
        mock_tab.page = mock_page
        mock_page.evaluate = AsyncMock(return_value={"width": 1920, "height": 1080})
        mock_page.mouse.move = AsyncMock()

        result = await vision_service.move_mouse(x=600, y=400, steps=15)

        assert result.success
        assert "Moved mouse to (600, 400)" in result.message
        assert result.data["steps"] == 15

        mock_page.mouse.move.assert_called_once_with(600, 400, steps=15)

    @pytest.mark.asyncio
    async def test_save_screenshot_with_directories(self, vision_service):
        """Test save screenshot with directory creation."""
        # Mock successful screenshot
        with patch.object(vision_service, "take_screenshot") as mock_take:
            mock_take.return_value = ServiceResult(
                success=True,
                message="Screenshot taken",
                data={"content": [{"data": b"test_screenshot_data"}], "format": "png"},
            )

            # Mock file operations
            with patch("builtins.open", create=True) as mock_open:
                with patch("pathlib.Path.mkdir") as mock_mkdir:
                    with patch("pathlib.Path.exists", return_value=True):
                        with patch("pathlib.Path.stat") as mock_stat:
                            mock_stat.return_value.st_size = 100

                            result = await vision_service.save_screenshot(
                                filename="test_dir/screenshot.png",
                                create_directories=True,
                            )

            assert result.success
            assert "Screenshot saved" in result.message
            mock_mkdir.assert_called_once()


class TestEnhancedVisionTools:
    """Test enhanced vision tools integration."""

    @pytest.fixture
    def mock_context(self):
        context = Mock()
        context.current_tab_or_die.return_value = Mock()
        context.client_supports_images.return_value = True
        context.settings.output_dir = Path("/tmp")
        return context

    @pytest.mark.asyncio
    async def test_browser_screenshot_tool(self, mock_context):
        """Test enhanced browser screenshot tool."""
        tool = browser_screenshot_factory(capture_snapshot=False)

        with patch.object(VisionService, "take_screenshot") as mock_service:
            mock_service.return_value = ServiceResult(
                success=True,
                message="Screenshot taken",
                data={
                    "has_screenshot": True,
                    "content": [{"data": b"screenshot_data"}],
                    "format": "png",
                },
            )

            result = await tool.handle(
                mock_context,
                {
                    "full_page": True,
                    "quality": 90,
                    "format": "jpeg",
                    "element_selector": "#test",
                },
            )

            assert result.code[0] == "# Take enhanced screenshot with advanced options"

            action_result = await result.action()
            assert action_result.content[0]["type"] == "text"
            assert len(action_result.content) >= 1

    @pytest.mark.asyncio
    async def test_browser_screen_click_tool(self, mock_context):
        """Test enhanced screen click tool."""
        tool = browser_screen_click_factory(capture_snapshot=False)

        with patch.object(VisionService, "screen_click") as mock_service:
            mock_service.return_value = ServiceResult(
                success=True, message="Clicked successfully", data={}
            )

            result = await tool.handle(
                mock_context,
                {
                    "x": 500,
                    "y": 300,
                    "element": "Test Button",
                    "click_type": "right",
                    "modifiers": ["Control", "Shift"],
                    "validate_bounds": True,
                },
            )

            assert "Advanced screen click" in result.code[0]
            assert any("Click type: right" in line for line in result.code)

            action_result = await result.action()
            assert action_result.content[0]["type"] == "text"

    @pytest.mark.asyncio
    async def test_vision_tools_collection(self):
        """Test that all vision tools are properly included."""
        all_tools = get_vision_tools()
        screenshot_tools = get_screenshot_tools()
        screen_tools = get_vision_screen_tools()

        assert len(all_tools) == 7  # All enhanced tools
        assert len(screenshot_tools) == 2  # Screenshot tools
        assert len(screen_tools) == 5  # Screen interaction tools

        tool_names = [tool.schema.name for tool in all_tools]
        expected_tools = [
            "browser_screenshot",
            "browser_save_screenshot",
            "browser_screen_click",
            "browser_screen_drag",
            "browser_screen_type",
            "browser_move_mouse",
            "browser_capture_snapshot",
        ]

        for expected in expected_tools:
            assert expected in tool_names

    @pytest.mark.asyncio
    async def test_schema_validation(self):
        """Test that schemas properly validate input."""
        # Test valid screenshot input
        valid_screenshot = ScreenshotInputSchema(
            full_page=True,
            quality=85,
            format="jpeg",
            clip_region={"x": 0, "y": 0, "width": 100, "height": 100},
        )
        assert valid_screenshot.quality == 85
        assert valid_screenshot.format == "jpeg"

        # Test invalid quality
        with pytest.raises(ValueError):
            ScreenshotInputSchema(quality=150, format="jpeg")

        # Test invalid clip region
        with pytest.raises(ValueError):
            ScreenshotInputSchema(
                clip_region={"x": 0, "y": 0, "width": -100, "height": 100}
            )

        # Test save screenshot validation
        valid_save = SaveScreenshotInputSchema(filename="test.png", overwrite=False)
        assert valid_save.filename == "test.png"

        # Test filename security
        with pytest.raises(ValueError):
            SaveScreenshotInputSchema(filename="../../../etc/passwd")


class TestVisionServiceEdgeCases:
    """Test edge cases and error conditions."""

    @pytest.fixture
    def mock_context(self):
        context = Mock()
        context.current_tab_or_die.return_value = Mock()
        context.settings.output_dir = Path("/tmp")
        return context

    @pytest.fixture
    def vision_service(self, mock_context):
        return VisionService(mock_context)

    @pytest.mark.asyncio
    async def test_coordinate_validation_edge_cases(self, vision_service):
        """Test coordinate validation with edge cases."""
        mock_tab = vision_service.context.current_tab_or_die.return_value
        mock_page = Mock()
        mock_tab.page = mock_page

        # Test negative coordinates
        mock_page.evaluate = AsyncMock(return_value={"width": 1920, "height": 1080})
        validation = await vision_service._validate_coordinates(-10, 50)
        assert not validation["valid"]
        assert "negative" in validation["reason"]

        # Test coordinates outside viewport
        validation = await vision_service._validate_coordinates(2000, 50)
        assert not validation["valid"]
        assert "outside viewport" in validation["reason"]

        # Test valid coordinates
        validation = await vision_service._validate_coordinates(500, 300)
        assert validation["valid"]

    @pytest.mark.asyncio
    async def test_error_handling_during_screenshot(self, vision_service):
        """Test error handling when screenshot fails."""
        mock_tab = vision_service.context.current_tab_or_die.return_value
        mock_page = Mock()
        mock_tab.page = mock_page
        mock_page.url = "https://example.com"
        mock_page.screenshot = AsyncMock(side_effect=Exception("Screenshot failed"))

        result = await vision_service.take_screenshot()

        assert not result.success
        assert "Failed to take screenshot" in result.message
        assert "Screenshot failed" in result.error

    @pytest.mark.asyncio
    async def test_iframe_error_handling(self, vision_service):
        """Test iframe error handling in coordinate validation."""
        mock_tab = vision_service.context.current_tab_or_die.return_value
        mock_page = Mock()
        mock_tab.page = mock_page
        mock_page.evaluate = AsyncMock(side_effect=Exception("Page evaluation failed"))

        validation = await vision_service._validate_coordinates(100, 100)
        assert not validation["valid"]
        assert "Failed to validate coordinates" in validation["reason"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
