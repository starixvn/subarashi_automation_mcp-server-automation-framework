import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import sys
from pathlib import Path

# Add the parent directory to the path so we can import from the main package
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.conftest import assert_text_content, assert_contains_text_content
from context import ServerContext
from config.settings import Config, get_default_config, config_to_settings
from tools.network import get_network_tools
from services.network_service import NetworkService
from services.base_service import ServiceResult


@pytest.mark.asyncio
async def test_browser_network_requests():
    # Test network request monitoring
    network_tools = get_network_tools(capture_snapshot=False)
    network_requests_tool = next(
        tool for tool in network_tools if tool.schema.name == "browser_network_requests"
    )

    # Mock service result with network requests
    mock_service_result = ServiceResult(
        success=True,
        message="Retrieved 4 network requests",
        data={
            "requests": [
                {
                    "url": "https://example.com/",
                    "method": "GET",
                    "status": 200,
                    "size": 1024,
                },
                {
                    "url": "https://example.com/style.css",
                    "method": "GET",
                    "status": 200,
                    "size": 2048,
                },
                {
                    "url": "https://example.com/script.js",
                    "method": "GET",
                    "status": 200,
                    "size": 4096,
                },
                {
                    "url": "https://api.example.com/data",
                    "method": "POST",
                    "status": 201,
                    "size": 512,
                },
            ],
            "count": 4,
        },
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(
        NetworkService, "get_network_requests", return_value=mock_service_result
    ):
        result = await network_requests_tool.handle(mock_context, {})

        # Test ToolResult structure
        assert result.code == [
            "# Get network requests from current tab",
            "# Returns list of HTTP requests made by the page",
        ]
        assert result.capture_snapshot is False
        assert result.wait_for_network is False
        assert result.action is not None

        # Test action execution
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        content_text = action_result.content[0]["text"]
        assert "### Network Requests" in content_text
        assert "**GET** https://example.com/" in content_text
        assert "**POST** https://api.example.com/data" in content_text


@pytest.mark.asyncio
async def test_browser_network_requests_empty():
    # Test network request monitoring with no requests
    network_tools = get_network_tools(capture_snapshot=False)
    network_requests_tool = next(
        tool for tool in network_tools if tool.schema.name == "browser_network_requests"
    )

    # Mock service result with no requests
    mock_service_result = ServiceResult(
        success=True,
        message="No network requests found",
        data={"requests": [], "count": 0},
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(
        NetworkService, "get_network_requests", return_value=mock_service_result
    ):
        result = await network_requests_tool.handle(mock_context, {})

        # Test action execution for empty requests
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert "No network requests" in action_result.content[0]["text"]


@pytest.mark.asyncio
async def test_browser_set_request_interception_enable():
    # Test enabling request interception
    network_tools = get_network_tools(capture_snapshot=False)
    set_interception_tool = next(
        tool
        for tool in network_tools
        if tool.schema.name == "browser_set_request_interception"
    )

    # Mock service result
    mock_service_result = ServiceResult(
        success=True,
        message="Request interception enabled successfully",
        data={"enabled": True, "patterns": ["**/*"], "intercepted_count": 0},
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(
        NetworkService, "set_request_interception", return_value=mock_service_result
    ):
        result = await set_interception_tool.handle(mock_context, {"enabled": True})

        # Test ToolResult structure
        assert result.code == ["# Set request interception", "# Enabled: True"]
        assert result.capture_snapshot is False
        assert result.wait_for_network is False
        assert result.action is not None

        # Test action execution
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert (
            "Request interception enabled successfully"
            in action_result.content[0]["text"]
        )


@pytest.mark.asyncio
async def test_browser_set_request_interception_disable():
    # Test disabling request interception
    network_tools = get_network_tools(capture_snapshot=False)
    set_interception_tool = next(
        tool
        for tool in network_tools
        if tool.schema.name == "browser_set_request_interception"
    )

    # Mock service result
    mock_service_result = ServiceResult(
        success=True,
        message="Request interception disabled successfully",
        data={"enabled": False, "patterns": [], "intercepted_count": 15},
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(
        NetworkService, "set_request_interception", return_value=mock_service_result
    ):
        result = await set_interception_tool.handle(mock_context, {"enabled": False})

        # Test ToolResult structure
        assert result.code == ["# Set request interception", "# Enabled: False"]
        assert result.capture_snapshot is False
        assert result.wait_for_network is False
        assert result.action is not None

        # Test action execution
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert (
            "Request interception disabled successfully"
            in action_result.content[0]["text"]
        )


@pytest.mark.asyncio
async def test_browser_set_request_interception_with_patterns():
    # Test request interception with specific patterns
    network_tools = get_network_tools(capture_snapshot=False)
    set_interception_tool = next(
        tool
        for tool in network_tools
        if tool.schema.name == "browser_set_request_interception"
    )

    # Mock service result
    mock_service_result = ServiceResult(
        success=True,
        message="Request interception enabled for patterns: **/api/**, **/*.css",
        data={
            "enabled": True,
            "patterns": ["**/api/**", "**/*.css"],
            "intercepted_count": 0,
        },
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(
        NetworkService, "set_request_interception", return_value=mock_service_result
    ):
        result = await set_interception_tool.handle(
            mock_context, {"enabled": True, "patterns": ["**/api/**", "**/*.css"]}
        )

        # Test action execution
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert (
            "Request interception enabled for patterns: **/api/**, **/*.css"
            in action_result.content[0]["text"]
        )


@pytest.mark.asyncio
async def test_browser_network_requests_with_filters():
    # Test network request monitoring with filters
    network_tools = get_network_tools(capture_snapshot=False)
    network_requests_tool = next(
        tool for tool in network_tools if tool.schema.name == "browser_network_requests"
    )

    # Mock service result with filtered requests
    mock_service_result = ServiceResult(
        success=True,
        message="Retrieved 2 POST requests",
        data={
            "requests": [
                {
                    "url": "https://api.example.com/login",
                    "method": "POST",
                    "status": 200,
                    "size": 256,
                },
                {
                    "url": "https://api.example.com/data",
                    "method": "POST",
                    "status": 200,
                    "size": 1024,
                },
            ],
            "count": 2,
            "filter": {"method": "POST", "status": 200},
        },
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(
        NetworkService, "get_network_requests", return_value=mock_service_result
    ):
        result = await network_requests_tool.handle(
            mock_context, {"method": "POST", "status": 200}
        )

        # Test action execution with filters
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        content_text = action_result.content[0]["text"]
        assert "### Network Requests" in content_text
        assert "**POST** https://api.example.com/login" in content_text
        assert "**POST** https://api.example.com/data" in content_text


@pytest.mark.asyncio
async def test_browser_network_requests_with_headers():
    # Test network request monitoring with headers
    network_tools = get_network_tools(capture_snapshot=False)
    network_requests_tool = next(
        tool for tool in network_tools if tool.schema.name == "browser_network_requests"
    )

    # Mock service result with headers
    mock_service_result = ServiceResult(
        success=True,
        message="Retrieved network requests with headers",
        data={
            "requests": [
                {
                    "url": "https://example.com/",
                    "method": "GET",
                    "status": 200,
                    "size": 1024,
                    "headers": {
                        "User-Agent": "Mozilla/5.0...",
                        "Accept": "text/html,application/xhtml+xml",
                    },
                },
                {
                    "url": "https://api.example.com/data",
                    "method": "POST",
                    "status": 201,
                    "size": 512,
                    "headers": {
                        "Content-Type": "application/json",
                        "Authorization": "Bearer token123",
                    },
                },
            ],
            "count": 2,
            "include_headers": True,
        },
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(
        NetworkService, "get_network_requests", return_value=mock_service_result
    ):
        result = await network_requests_tool.handle(
            mock_context, {"include_headers": True}
        )

        # Test action execution with headers
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        content_text = action_result.content[0]["text"]
        assert "### Network Requests" in content_text
        assert "**GET** https://example.com/" in content_text
        assert "**POST** https://api.example.com/data" in content_text


@pytest.mark.asyncio
async def test_browser_network_requests_error_handling():
    # Test error handling in network requests
    network_tools = get_network_tools(capture_snapshot=False)
    network_requests_tool = next(
        tool for tool in network_tools if tool.schema.name == "browser_network_requests"
    )

    # Mock service error result
    mock_service_result = ServiceResult(
        success=False,
        message="Network monitoring not enabled",
        error="Network monitoring not enabled",
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(
        NetworkService, "get_network_requests", return_value=mock_service_result
    ):
        result = await network_requests_tool.handle(mock_context, {})

        # Test action execution with error
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert "Network monitoring not enabled" in action_result.content[0]["text"]


@pytest.mark.asyncio
async def test_browser_set_request_interception_error():
    # Test error handling in request interception
    network_tools = get_network_tools(capture_snapshot=False)
    set_interception_tool = next(
        tool
        for tool in network_tools
        if tool.schema.name == "browser_set_request_interception"
    )

    # Mock service error result
    mock_service_result = ServiceResult(
        success=False,
        message="Failed to set request interception",
        error="Browser context not available",
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(
        NetworkService, "set_request_interception", return_value=mock_service_result
    ):
        result = await set_interception_tool.handle(mock_context, {"enabled": True})

        # Test action execution with error
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert "Failed to set request interception" in action_result.content[0]["text"]


@pytest.mark.asyncio
async def test_network_capability_filtering():
    # Test that network tools have proper capability filtering
    network_tools = get_network_tools(capture_snapshot=False)

    # Check that we have the expected network tools
    tool_names = [tool.schema.name for tool in network_tools]
    expected_tools = ["browser_network_requests", "browser_set_request_interception"]

    for expected_tool in expected_tools:
        assert expected_tool in tool_names, f"Missing network tool: {expected_tool}"

    # Check that all tools have NETWORK capability
    from core.tool_schema import ToolCapability

    for tool in network_tools:
        assert tool.capability == ToolCapability.NETWORK


@pytest.mark.asyncio
async def test_network_tools_capture_snapshot_parameter():
    # Test that network tools respect capture_snapshot parameter
    tools_with_snapshot = get_network_tools(capture_snapshot=True)
    tools_without_snapshot = get_network_tools(capture_snapshot=False)

    # Find network requests tool in both sets
    requests_with_snapshot = next(
        tool
        for tool in tools_with_snapshot
        if tool.schema.name == "browser_network_requests"
    )
    requests_without_snapshot = next(
        tool
        for tool in tools_without_snapshot
        if tool.schema.name == "browser_network_requests"
    )

    # Create mock context and service result
    mock_context = MagicMock()
    mock_service_result = ServiceResult(
        success=True,
        message="Retrieved network requests",
        data={"requests": [], "count": 0},
    )

    with patch.object(
        NetworkService, "get_network_requests", return_value=mock_service_result
    ):
        result_with_snapshot = await requests_with_snapshot.handle(mock_context, {})
        result_without_snapshot = await requests_without_snapshot.handle(
            mock_context, {}
        )

        assert result_with_snapshot.capture_snapshot is True
        assert result_without_snapshot.capture_snapshot is False


@pytest.mark.asyncio
async def test_network_tools_schema_validation():
    # Test that network tools have proper schema validation
    network_tools = get_network_tools(capture_snapshot=False)

    for tool in network_tools:
        assert tool.schema.name is not None
        assert tool.schema.title is not None
        assert tool.schema.description is not None
        assert tool.schema.input_schema is not None
        assert tool.schema.tool_type is not None
        assert tool.handle is not None
        assert tool.capability is not None

        # Test that tools have proper type
        from core.tool_schema import ToolType

        if tool.schema.name == "browser_network_requests":
            assert tool.schema.tool_type == ToolType.READ_ONLY
        elif tool.schema.name == "browser_set_request_interception":
            assert tool.schema.tool_type == ToolType.DESTRUCTIVE


@pytest.mark.asyncio
async def test_network_tools_network_settings():
    # Test that network tools have proper network settings
    network_tools = get_network_tools(capture_snapshot=False)

    for tool in network_tools:
        mock_context = MagicMock()
        mock_service_result = ServiceResult(
            success=True, message="Operation successful", data={}
        )

        with patch.object(
            NetworkService, "get_network_requests", return_value=mock_service_result
        ):
            with patch.object(
                NetworkService,
                "set_request_interception",
                return_value=mock_service_result,
            ):
                if tool.schema.name == "browser_network_requests":
                    result = await tool.handle(mock_context, {})
                else:
                    result = await tool.handle(mock_context, {"enabled": True})

                # Network operations shouldn't wait for network
                assert result.wait_for_network is False


@pytest.mark.asyncio
async def test_network_request_performance_metrics():
    # Test network request performance metrics
    network_tools = get_network_tools(capture_snapshot=False)
    network_requests_tool = next(
        tool for tool in network_tools if tool.schema.name == "browser_network_requests"
    )

    # Mock service result with performance metrics
    mock_service_result = ServiceResult(
        success=True,
        message="Retrieved network requests with performance metrics",
        data={
            "requests": [
                {
                    "url": "https://example.com/",
                    "method": "GET",
                    "status": 200,
                    "size": 1024,
                    "timing": {
                        "dns": 50,
                        "connect": 100,
                        "request": 200,
                        "response": 300,
                        "total": 650,
                    },
                }
            ],
            "count": 1,
            "include_performance": True,
        },
    )

    # Create mock context
    mock_context = MagicMock()

    with patch.object(
        NetworkService, "get_network_requests", return_value=mock_service_result
    ):
        result = await network_requests_tool.handle(
            mock_context, {"include_performance": True}
        )

        # Test action execution with performance metrics
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        content_text = action_result.content[0]["text"]
        assert "### Network Requests" in content_text
        assert "**GET** https://example.com/" in content_text
