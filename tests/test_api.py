import pytest
from tools.api import get_api_tools
from core.schemas import ApiRequestInputSchema
from context import ServerContext
from config.settings import Settings


@pytest.fixture
def context():
    settings = Settings(headless=True)
    return ServerContext(settings)


@pytest.fixture
def api_tools():
    return get_api_tools(capture_snapshot=False)


class TestApiTools:
    def test_api_tools_creation(self, api_tools):
        assert len(api_tools) == 1
        tool_names = [tool.schema.name for tool in api_tools]
        expected_names = [
            "api_request",
        ]
        assert set(tool_names) == set(expected_names)

    def test_api_request_schema_validation(self):
        valid_params = {"url": "https://api.example.com/test", "method": "GET"}
        schema = ApiRequestInputSchema(**valid_params)
        assert schema.url == "https://api.example.com/test"
        assert schema.method == "GET"
        assert schema.timeout == 30

    def test_api_request_schema_validation_invalid_url(self):
        invalid_params = {"url": "invalid-url", "method": "GET"}
        with pytest.raises(ValueError):
            ApiRequestInputSchema(**invalid_params)

    def test_api_request_schema_validation_invalid_method(self):
        invalid_params = {"url": "https://api.example.com/test", "method": "INVALID"}
        with pytest.raises(ValueError):
            ApiRequestInputSchema(**invalid_params)

    def test_api_tools_have_correct_capabilities(self, api_tools):
        from core.tool_schema import ToolCapability

        for tool in api_tools:
            assert tool.capability == ToolCapability.API

    def test_api_tools_have_correct_schemas(self, api_tools):
        for tool in api_tools:
            assert tool.schema.name.startswith("api_")
            assert tool.schema.input_schema == ApiRequestInputSchema

    def test_api_request_tool_structure(self, api_tools):
        api_request_tool = next(
            tool for tool in api_tools if tool.schema.name == "api_request"
        )
        assert api_request_tool.schema.name == "api_request"
        assert hasattr(api_request_tool, "handle")

    @pytest.mark.asyncio
    async def test_api_request_tool_execution(self, context, api_tools):
        api_request_tool = next(
            tool for tool in api_tools if tool.schema.name == "api_request"
        )

        params = {"url": "https://httpbin.org/get", "method": "GET"}

        result = await api_request_tool.handle(context, params)

        assert result.code is not None
        assert len(result.code) > 0
        assert result.action is not None
        assert result.capture_snapshot is False
        assert result.wait_for_network is False


class TestApiRequestInputSchema:
    def test_api_request_schema_headers_parsing(self):
        # Test with dict headers
        params_dict = {
            "url": "https://api.example.com/test",
            "method": "POST",
            "headers": {
                "Content-Type": "application/json",
                "Authorization": "Bearer token123",
            },
        }
        schema = ApiRequestInputSchema(**params_dict)
        assert isinstance(schema.headers, dict)
        assert schema.headers["Content-Type"] == "application/json"
        assert schema.headers["Authorization"] == "Bearer token123"

    def test_api_request_schema_method_validation(self):
        valid_methods = ["GET", "POST", "PUT", "DELETE", "PATCH"]
        for method in valid_methods:
            params = {"url": "https://api.example.com/test", "method": method}
            schema = ApiRequestInputSchema(**params)
            assert schema.method == method

    def test_api_request_schema_timeout_validation(self):
        params = {"url": "https://api.example.com/test", "method": "GET", "timeout": 60}
        schema = ApiRequestInputSchema(**params)
        assert schema.timeout == 60

    def test_api_request_schema_body_validation(self):
        params = {
            "url": "https://api.example.com/test",
            "method": "POST",
            "body": '{"key": "value"}',
        }
        schema = ApiRequestInputSchema(**params)
        assert schema.body == '{"key": "value"}'


@pytest.mark.asyncio
async def test_api_tools_capability_filtering():
    # Test that api tools have proper capability filtering
    api_tools = get_api_tools(capture_snapshot=False)

    # Check that we have the expected api tools
    tool_names = [tool.schema.name for tool in api_tools]
    expected_tools = ["api_request"]

    for expected_tool in expected_tools:
        assert expected_tool in tool_names, f"Missing api tool: {expected_tool}"

    # Check that all tools have API capability
    from core.tool_schema import ToolCapability

    for tool in api_tools:
        assert tool.capability == ToolCapability.API


@pytest.mark.asyncio
async def test_api_tools_capture_snapshot_parameter():
    # Test that api tools respect capture_snapshot parameter
    tools_with_snapshot = get_api_tools(capture_snapshot=True)
    tools_without_snapshot = get_api_tools(capture_snapshot=False)

    assert len(tools_with_snapshot) == len(tools_without_snapshot)

    for tool in tools_with_snapshot:
        assert tool.schema.name.startswith("api_")

    for tool in tools_without_snapshot:
        assert tool.schema.name.startswith("api_")


@pytest.mark.asyncio
async def test_api_tools_schema_validation():
    # Test that api tools have proper schema validation
    api_tools = get_api_tools(capture_snapshot=False)

    for tool in api_tools:
        # Test that each tool has required attributes
        assert hasattr(tool, "schema")
        assert hasattr(tool.schema, "name")
        assert hasattr(tool.schema, "description")
        assert hasattr(tool.schema, "input_schema")

        # Test that api tools have read-only type
        from core.tool_schema import ToolType

        assert tool.schema.tool_type == ToolType.READ_ONLY


@pytest.mark.asyncio
async def test_api_tools_network_settings():
    # Test that api tools have proper network settings
    api_tools = get_api_tools(capture_snapshot=False)

    for tool in api_tools:
        # API tools should be browser independent
        assert getattr(tool, "browser_independent", False) == True
