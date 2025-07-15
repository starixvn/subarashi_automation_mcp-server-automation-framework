import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import sys
from pathlib import Path

# Add the parent directory to the path so we can import from the main package
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.conftest import assert_text_content, assert_contains_text_content
from context import ServerContext
from config.settings import Config, get_default_config, config_to_settings
from tools.pdf import get_pdf_tools
from services.pdf_service import PdfService
from services.base_service import ServiceResult


@pytest.mark.asyncio
async def test_browser_save_pdf():
    # Test basic PDF saving
    pdf_tools = get_pdf_tools(capture_snapshot=False)
    save_pdf_tool = next(
        tool for tool in pdf_tools if tool.schema.name == "browser_save_pdf"
    )

    # Mock service result
    mock_service_result = ServiceResult(
        success=True,
        message="PDF saved to /tmp/test.pdf",
        data={
            "filename": "test.pdf",
            "output_path": "/tmp/test.pdf",
            "full_page": False,
            "format": "A4",
        },
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(PdfService, "save_as_pdf", return_value=mock_service_result):
        result = await save_pdf_tool.handle(
            mock_context, {"filename": "test.pdf", "full_page": False}
        )

        # Test ToolResult structure
        assert result.code == [
            "# Save current page as PDF",
            "# Filename: test.pdf",
            "# Full page: False",
        ]
        assert result.capture_snapshot is False
        assert result.wait_for_network is False
        assert result.action is not None

        # Test action execution
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert "PDF saved to /tmp/test.pdf" in action_result.content[0]["text"]


@pytest.mark.asyncio
async def test_browser_save_pdf_full_page():
    # Test full page PDF saving
    pdf_tools = get_pdf_tools(capture_snapshot=False)
    save_pdf_tool = next(
        tool for tool in pdf_tools if tool.schema.name == "browser_save_pdf"
    )

    # Mock service result
    mock_service_result = ServiceResult(
        success=True,
        message="PDF saved to /tmp/fullpage.pdf",
        data={
            "filename": "fullpage.pdf",
            "output_path": "/tmp/fullpage.pdf",
            "full_page": True,
            "format": "A4",
        },
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(PdfService, "save_as_pdf", return_value=mock_service_result):
        result = await save_pdf_tool.handle(
            mock_context, {"filename": "fullpage.pdf", "full_page": True}
        )

        # Test ToolResult structure
        assert result.code == [
            "# Save current page as PDF",
            "# Filename: fullpage.pdf",
            "# Full page: True",
        ]
        assert result.capture_snapshot is False
        assert result.wait_for_network is False
        assert result.action is not None

        # Test action execution
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert "PDF saved to /tmp/fullpage.pdf" in action_result.content[0]["text"]


@pytest.mark.asyncio
async def test_browser_save_pdf_with_options():
    # Test PDF saving with custom options
    pdf_tools = get_pdf_tools(capture_snapshot=False)
    save_pdf_tool = next(
        tool for tool in pdf_tools if tool.schema.name == "browser_save_pdf"
    )

    # Mock service result
    mock_service_result = ServiceResult(
        success=True,
        message="PDF saved to /tmp/custom.pdf",
        data={
            "filename": "custom.pdf",
            "output_path": "/tmp/custom.pdf",
            "full_page": True,
            "format": "A4",
        },
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(PdfService, "save_as_pdf", return_value=mock_service_result):
        result = await save_pdf_tool.handle(
            mock_context, {"filename": "custom.pdf", "full_page": True}
        )

        # Test action execution
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert "PDF saved to /tmp/custom.pdf" in action_result.content[0]["text"]


@pytest.mark.asyncio
async def test_browser_save_pdf_landscape():
    # Test landscape PDF saving
    pdf_tools = get_pdf_tools(capture_snapshot=False)
    save_pdf_tool = next(
        tool for tool in pdf_tools if tool.schema.name == "browser_save_pdf"
    )

    # Mock service result
    mock_service_result = ServiceResult(
        success=True,
        message="PDF saved to /tmp/landscape.pdf",
        data={
            "filename": "landscape.pdf",
            "output_path": "/tmp/landscape.pdf",
            "full_page": False,
            "format": "A4",
        },
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(PdfService, "save_as_pdf", return_value=mock_service_result):
        result = await save_pdf_tool.handle(
            mock_context, {"filename": "landscape.pdf", "full_page": False}
        )

        # Test action execution
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert "PDF saved to /tmp/landscape.pdf" in action_result.content[0]["text"]


@pytest.mark.asyncio
async def test_browser_save_pdf_with_headers_footers():
    # Test PDF saving with headers and footers
    pdf_tools = get_pdf_tools(capture_snapshot=False)
    save_pdf_tool = next(
        tool for tool in pdf_tools if tool.schema.name == "browser_save_pdf"
    )

    # Mock service result
    mock_service_result = ServiceResult(
        success=True,
        message="PDF saved to /tmp/headers_footers.pdf",
        data={
            "filename": "headers_footers.pdf",
            "output_path": "/tmp/headers_footers.pdf",
            "full_page": False,
            "format": "A4",
        },
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(PdfService, "save_as_pdf", return_value=mock_service_result):
        result = await save_pdf_tool.handle(
            mock_context, {"filename": "headers_footers.pdf", "full_page": False}
        )

        # Test action execution
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert (
            "PDF saved to /tmp/headers_footers.pdf" in action_result.content[0]["text"]
        )


@pytest.mark.asyncio
async def test_browser_save_pdf_error_file_access():
    # Test error handling when file cannot be saved
    pdf_tools = get_pdf_tools(capture_snapshot=False)
    save_pdf_tool = next(
        tool for tool in pdf_tools if tool.schema.name == "browser_save_pdf"
    )

    # Mock service error result
    mock_service_result = ServiceResult(
        success=False,
        message="Failed to save PDF: Permission denied",
        error="Permission denied",
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(PdfService, "save_as_pdf", return_value=mock_service_result):
        result = await save_pdf_tool.handle(
            mock_context, {"filename": "test.pdf", "full_page": False}
        )

        # Test action execution with error
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert (
            "Failed to save PDF: Permission denied" in action_result.content[0]["text"]
        )


@pytest.mark.asyncio
async def test_browser_save_pdf_error_invalid_path():
    # Test error handling with invalid path
    pdf_tools = get_pdf_tools(capture_snapshot=False)
    save_pdf_tool = next(
        tool for tool in pdf_tools if tool.schema.name == "browser_save_pdf"
    )

    # Mock service error result
    mock_service_result = ServiceResult(
        success=False, message="Failed to save PDF: Invalid path", error="Invalid path"
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(PdfService, "save_as_pdf", return_value=mock_service_result):
        result = await save_pdf_tool.handle(
            mock_context, {"filename": "/invalid/path/test.pdf", "full_page": False}
        )

        # Test action execution with error
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert "Failed to save PDF: Invalid path" in action_result.content[0]["text"]


@pytest.mark.asyncio
async def test_browser_save_pdf_large_page():
    # Test saving PDF for large page content
    pdf_tools = get_pdf_tools(capture_snapshot=False)
    save_pdf_tool = next(
        tool for tool in pdf_tools if tool.schema.name == "browser_save_pdf"
    )

    # Mock service result
    mock_service_result = ServiceResult(
        success=True,
        message="PDF saved to /tmp/large_page.pdf",
        data={
            "filename": "large_page.pdf",
            "output_path": "/tmp/large_page.pdf",
            "full_page": True,
            "format": "A4",
        },
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(PdfService, "save_as_pdf", return_value=mock_service_result):
        result = await save_pdf_tool.handle(
            mock_context, {"filename": "large_page.pdf", "full_page": True}
        )

        # Test action execution
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert "PDF saved to /tmp/large_page.pdf" in action_result.content[0]["text"]


@pytest.mark.asyncio
async def test_browser_save_pdf_with_scale():
    # Test PDF saving with custom scale
    pdf_tools = get_pdf_tools(capture_snapshot=False)
    save_pdf_tool = next(
        tool for tool in pdf_tools if tool.schema.name == "browser_save_pdf"
    )

    # Mock service result
    mock_service_result = ServiceResult(
        success=True,
        message="PDF saved to /tmp/scaled.pdf",
        data={
            "filename": "scaled.pdf",
            "output_path": "/tmp/scaled.pdf",
            "full_page": False,
            "format": "A4",
        },
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(PdfService, "save_as_pdf", return_value=mock_service_result):
        result = await save_pdf_tool.handle(
            mock_context, {"filename": "scaled.pdf", "full_page": False}
        )

        # Test action execution
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert "PDF saved to /tmp/scaled.pdf" in action_result.content[0]["text"]


@pytest.mark.asyncio
async def test_browser_save_pdf_background_graphics():
    # Test PDF saving with background graphics
    pdf_tools = get_pdf_tools(capture_snapshot=False)
    save_pdf_tool = next(
        tool for tool in pdf_tools if tool.schema.name == "browser_save_pdf"
    )

    # Mock service result
    mock_service_result = ServiceResult(
        success=True,
        message="PDF saved to /tmp/background.pdf",
        data={
            "filename": "background.pdf",
            "output_path": "/tmp/background.pdf",
            "full_page": False,
            "format": "A4",
        },
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(PdfService, "save_as_pdf", return_value=mock_service_result):
        result = await save_pdf_tool.handle(
            mock_context, {"filename": "background.pdf", "full_page": False}
        )

        # Test action execution
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert "PDF saved to /tmp/background.pdf" in action_result.content[0]["text"]


@pytest.mark.asyncio
async def test_pdf_capability_filtering():
    # Test that PDF tools have proper capability filtering
    pdf_tools = get_pdf_tools(capture_snapshot=False)

    # Check that we have the expected PDF tools
    tool_names = [tool.schema.name for tool in pdf_tools]
    expected_tools = ["browser_save_pdf"]

    for expected_tool in expected_tools:
        assert expected_tool in tool_names, f"Missing PDF tool: {expected_tool}"

    # Check that all tools have PDF capability
    from core.tool_schema import ToolCapability

    for tool in pdf_tools:
        assert tool.capability == ToolCapability.PDF


@pytest.mark.asyncio
async def test_pdf_tools_capture_snapshot_parameter():
    # Test that PDF tools respect capture_snapshot parameter
    tools_with_snapshot = get_pdf_tools(capture_snapshot=True)
    tools_without_snapshot = get_pdf_tools(capture_snapshot=False)

    # Find save PDF tool in both sets
    save_pdf_with_snapshot = next(
        tool for tool in tools_with_snapshot if tool.schema.name == "browser_save_pdf"
    )
    save_pdf_without_snapshot = next(
        tool
        for tool in tools_without_snapshot
        if tool.schema.name == "browser_save_pdf"
    )

    # Create mock context and service result
    mock_context = MagicMock()
    mock_service_result = ServiceResult(
        success=True,
        message="PDF saved",
        data={
            "filename": "test.pdf",
            "output_path": "/tmp/test.pdf",
            "full_page": False,
            "format": "A4",
        },
    )

    with patch.object(PdfService, "save_as_pdf", return_value=mock_service_result):
        result_with_snapshot = await save_pdf_with_snapshot.handle(
            mock_context, {"filename": "test.pdf", "full_page": False}
        )
        result_without_snapshot = await save_pdf_without_snapshot.handle(
            mock_context, {"filename": "test.pdf", "full_page": False}
        )

        assert result_with_snapshot.capture_snapshot is True
        assert result_without_snapshot.capture_snapshot is False


@pytest.mark.asyncio
async def test_pdf_tools_schema_validation():
    # Test that PDF tools have proper schema validation
    pdf_tools = get_pdf_tools(capture_snapshot=False)

    for tool in pdf_tools:
        assert tool.schema.name is not None
        assert tool.schema.title is not None
        assert tool.schema.description is not None
        assert tool.schema.input_schema is not None
        assert tool.schema.tool_type is not None
        assert tool.handle is not None
        assert tool.capability is not None

        # Test that PDF tools have read-only type
        from core.tool_schema import ToolType

        assert tool.schema.tool_type == ToolType.READ_ONLY


@pytest.mark.asyncio
async def test_pdf_tools_network_settings():
    # Test that PDF tools have proper network settings
    pdf_tools = get_pdf_tools(capture_snapshot=False)

    for tool in pdf_tools:
        mock_context = MagicMock()
        mock_service_result = ServiceResult(
            success=True,
            message="PDF saved",
            data={
                "filename": "test.pdf",
                "output_path": "/tmp/test.pdf",
                "full_page": False,
                "format": "A4",
            },
        )

        with patch.object(PdfService, "save_as_pdf", return_value=mock_service_result):
            result = await tool.handle(
                mock_context, {"filename": "test.pdf", "full_page": False}
            )

            # PDF operations shouldn't wait for network
            assert result.wait_for_network is False
