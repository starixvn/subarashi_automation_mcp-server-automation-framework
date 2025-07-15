import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from pathlib import Path
import sys

# Add the parent directory to the path so we can import from the main package
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.conftest import assert_text_content, assert_contains_text_content
from context import ServerContext
from config.settings import Config, get_default_config, config_to_settings
from tools.files import get_file_tools
from services.files_service import FilesService
from services.base_service import ServiceResult


@pytest.mark.asyncio
async def test_browser_upload_file_single():
    # Test single file upload
    file_tools = get_file_tools(capture_snapshot=True)
    upload_tool = next(
        tool for tool in file_tools if tool.schema.name == "browser_upload_file"
    )

    # Mock service result
    mock_service_result = ServiceResult(
        success=True,
        message="Successfully uploaded file: /tmp/test.txt",
        data={"files": ["/tmp/test.txt"], "count": 1},
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(FilesService, "upload_files", return_value=mock_service_result):
        result = await upload_tool.handle(
            mock_context, {"file_paths": ["/tmp/test.txt"]}
        )

        # Test ToolResult structure
        assert result.code == [
            "# Upload files to file chooser",
            "# Files: ['/tmp/test.txt']",
        ]
        assert result.capture_snapshot is True
        assert result.wait_for_network is True
        assert result.action is not None

        # Test action execution
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert (
            "Successfully uploaded file: /tmp/test.txt"
            in action_result.content[0]["text"]
        )


@pytest.mark.asyncio
async def test_browser_upload_file_multiple():
    # Test multiple file upload
    file_tools = get_file_tools(capture_snapshot=True)
    upload_tool = next(
        tool for tool in file_tools if tool.schema.name == "browser_upload_file"
    )

    file_paths = ["/tmp/file1.pdf", "/tmp/file2.jpg", "/tmp/file3.doc"]

    # Mock service result
    mock_service_result = ServiceResult(
        success=True,
        message="Successfully uploaded 3 files",
        data={"files": file_paths, "count": 3},
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(FilesService, "upload_files", return_value=mock_service_result):
        result = await upload_tool.handle(mock_context, {"file_paths": file_paths})

        # Test ToolResult structure
        assert result.code == [
            "# Upload files to file chooser",
            f"# Files: {file_paths}",
        ]
        assert result.capture_snapshot is True
        assert result.wait_for_network is True
        assert result.action is not None

        # Test action execution
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert "Successfully uploaded 3 files" in action_result.content[0]["text"]


@pytest.mark.asyncio
async def test_browser_upload_file_error_file_not_found():
    # Test error handling for file not found
    file_tools = get_file_tools(capture_snapshot=True)
    upload_tool = next(
        tool for tool in file_tools if tool.schema.name == "browser_upload_file"
    )

    # Mock service error result
    mock_service_result = ServiceResult(
        success=False,
        message="File not found: /tmp/nonexistent.txt",
        error="File not found",
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(FilesService, "upload_files", return_value=mock_service_result):
        result = await upload_tool.handle(
            mock_context, {"file_paths": ["/tmp/nonexistent.txt"]}
        )

        # Test action execution with error
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert (
            "File not found: /tmp/nonexistent.txt" in action_result.content[0]["text"]
        )


@pytest.mark.asyncio
async def test_browser_upload_file_error_no_file_input():
    # Test error handling for no file input element
    file_tools = get_file_tools(capture_snapshot=True)
    upload_tool = next(
        tool for tool in file_tools if tool.schema.name == "browser_upload_file"
    )

    # Mock service error result
    mock_service_result = ServiceResult(
        success=False,
        message="No file input element found on page",
        error="No file input element found",
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(FilesService, "upload_files", return_value=mock_service_result):
        result = await upload_tool.handle(
            mock_context, {"file_paths": ["/tmp/test.txt"]}
        )

        # Test action execution with error
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert "No file input element found on page" in action_result.content[0]["text"]


@pytest.mark.asyncio
async def test_browser_upload_file_image_types():
    # Test uploading different image file types
    file_tools = get_file_tools(capture_snapshot=True)
    upload_tool = next(
        tool for tool in file_tools if tool.schema.name == "browser_upload_file"
    )

    image_files = ["/tmp/photo.jpg", "/tmp/logo.png", "/tmp/avatar.gif"]

    # Mock service result
    mock_service_result = ServiceResult(
        success=True,
        message="Successfully uploaded 3 image files",
        data={"files": image_files, "count": 3, "types": ["JPEG", "PNG", "GIF"]},
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(FilesService, "upload_files", return_value=mock_service_result):
        result = await upload_tool.handle(mock_context, {"file_paths": image_files})

        # Test action execution
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert "Successfully uploaded 3 image files" in action_result.content[0]["text"]


@pytest.mark.asyncio
async def test_browser_upload_file_document_types():
    # Test uploading different document file types
    file_tools = get_file_tools(capture_snapshot=True)
    upload_tool = next(
        tool for tool in file_tools if tool.schema.name == "browser_upload_file"
    )

    document_files = ["/tmp/report.pdf", "/tmp/data.csv", "/tmp/notes.txt"]

    # Mock service result
    mock_service_result = ServiceResult(
        success=True,
        message="Successfully uploaded 3 document files",
        data={
            "files": document_files,
            "count": 3,
            "sizes": ["2.5 MB", "1.2 MB", "0.5 MB"],
        },
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(FilesService, "upload_files", return_value=mock_service_result):
        result = await upload_tool.handle(mock_context, {"file_paths": document_files})

        # Test action execution
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert (
            "Successfully uploaded 3 document files" in action_result.content[0]["text"]
        )


@pytest.mark.asyncio
async def test_browser_upload_file_large_files():
    # Test uploading large files
    file_tools = get_file_tools(capture_snapshot=True)
    upload_tool = next(
        tool for tool in file_tools if tool.schema.name == "browser_upload_file"
    )

    large_files = ["/tmp/large_file.zip"]

    # Mock service result
    mock_service_result = ServiceResult(
        success=True,
        message="Successfully uploaded large file (15.2 MB)",
        data={
            "files": large_files,
            "count": 1,
            "size": "15.2 MB",
            "validation": {
                "size_check": "passed",
                "type_check": "passed",
                "virus_scan": "clean",
            },
        },
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(FilesService, "upload_files", return_value=mock_service_result):
        result = await upload_tool.handle(mock_context, {"file_paths": large_files})

        # Test action execution
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert (
            "Successfully uploaded large file (15.2 MB)"
            in action_result.content[0]["text"]
        )


@pytest.mark.asyncio
async def test_browser_upload_file_with_progress():
    # Test file upload with progress tracking
    file_tools = get_file_tools(capture_snapshot=True)
    upload_tool = next(
        tool for tool in file_tools if tool.schema.name == "browser_upload_file"
    )

    video_files = ["/tmp/video.mp4"]

    # Mock service result
    mock_service_result = ServiceResult(
        success=True,
        message="Successfully uploaded video file",
        data={
            "files": video_files,
            "count": 1,
            "size": "50.2 MB",
            "upload_time": "12.5 seconds",
            "speed": "4.02 MB/s",
        },
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(FilesService, "upload_files", return_value=mock_service_result):
        result = await upload_tool.handle(mock_context, {"file_paths": video_files})

        # Test action execution
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert "Successfully uploaded video file" in action_result.content[0]["text"]


@pytest.mark.asyncio
async def test_files_capability_filtering():
    # Test that file tools have proper capability filtering
    file_tools = get_file_tools(capture_snapshot=True)

    # Check that we have the expected file tools
    tool_names = [tool.schema.name for tool in file_tools]
    expected_tools = ["browser_upload_file"]

    for expected_tool in expected_tools:
        assert expected_tool in tool_names, f"Missing file tool: {expected_tool}"

    # Check that all tools have FILES capability
    from core.tool_schema import ToolCapability

    for tool in file_tools:
        assert tool.capability == ToolCapability.FILES


@pytest.mark.asyncio
async def test_file_tools_capture_snapshot_parameter():
    # Test that file tools respect capture_snapshot parameter
    tools_with_snapshot = get_file_tools(capture_snapshot=True)
    tools_without_snapshot = get_file_tools(capture_snapshot=False)

    # Find upload tool in both sets
    upload_with_snapshot = next(
        tool
        for tool in tools_with_snapshot
        if tool.schema.name == "browser_upload_file"
    )
    upload_without_snapshot = next(
        tool
        for tool in tools_without_snapshot
        if tool.schema.name == "browser_upload_file"
    )

    # Create mock context and service result
    mock_context = MagicMock()
    mock_service_result = ServiceResult(
        success=True,
        message="Successfully uploaded file",
        data={"files": ["/tmp/test.txt"], "count": 1},
    )

    with patch.object(FilesService, "upload_files", return_value=mock_service_result):
        result_with_snapshot = await upload_with_snapshot.handle(
            mock_context, {"file_paths": ["/tmp/test.txt"]}
        )
        result_without_snapshot = await upload_without_snapshot.handle(
            mock_context, {"file_paths": ["/tmp/test.txt"]}
        )

        assert result_with_snapshot.capture_snapshot is True
        assert result_without_snapshot.capture_snapshot is False


@pytest.mark.asyncio
async def test_file_tools_schema_validation():
    # Test that file tools have proper schema validation
    file_tools = get_file_tools(capture_snapshot=True)

    for tool in file_tools:
        assert tool.schema.name is not None
        assert tool.schema.title is not None
        assert tool.schema.description is not None
        assert tool.schema.input_schema is not None
        assert tool.schema.tool_type is not None
        assert tool.handle is not None
        assert tool.capability is not None

        # Test that file tools have destructive type (they change page state)
        from core.tool_schema import ToolType

        assert tool.schema.tool_type == ToolType.DESTRUCTIVE


@pytest.mark.asyncio
async def test_file_tools_clears_modal_state():
    # Test that file upload tool clears modal state
    file_tools = get_file_tools(capture_snapshot=True)
    upload_tool = next(
        tool for tool in file_tools if tool.schema.name == "browser_upload_file"
    )

    # Check that upload tool has clears_modal_state attribute
    assert hasattr(upload_tool, "clears_modal_state")
    assert upload_tool.clears_modal_state == "fileChooser"


@pytest.mark.asyncio
async def test_file_upload_empty_file_list():
    # Test error handling with empty file list (schema validation)
    file_tools = get_file_tools(capture_snapshot=True)
    upload_tool = next(
        tool for tool in file_tools if tool.schema.name == "browser_upload_file"
    )

    # Create mock context
    mock_context = MagicMock()

    # Test that schema validation catches empty file list
    with pytest.raises(Exception) as exc_info:
        await upload_tool.handle(mock_context, {"file_paths": []})

    # Verify it's a validation error about empty file list
    assert "At least one file path must be provided" in str(exc_info.value)
