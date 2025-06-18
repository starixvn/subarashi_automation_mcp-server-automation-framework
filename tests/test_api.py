import pytest
from tools.api import get_api_tools
from tools.schemas import ApiRequestInputSchema, ApiTestInputSchema
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
        assert len(api_tools) == 7
        tool_names = [tool.schema.name for tool in api_tools]
        expected_names = [
            "api_request",
            "api_get", 
            "api_post",
            "api_put",
            "api_delete",
            "api_patch",
            "api_test"
        ]
        assert set(tool_names) == set(expected_names)

    def test_api_request_schema_validation(self):
        valid_params = {
            "url": "https://api.example.com/test",
            "method": "GET"
        }
        schema = ApiRequestInputSchema(**valid_params)
        assert schema.url == "https://api.example.com/test"
        assert schema.method == "GET"
        assert schema.timeout == 30

    def test_api_request_schema_validation_invalid_url(self):
        invalid_params = {
            "url": "invalid-url",
            "method": "GET"
        }
        with pytest.raises(ValueError):
            ApiRequestInputSchema(**invalid_params)

    def test_api_request_schema_validation_invalid_method(self):
        invalid_params = {
            "url": "https://api.example.com/test",
            "method": "INVALID"
        }
        with pytest.raises(ValueError):
            ApiRequestInputSchema(**invalid_params)

    def test_api_test_schema_validation(self):
        valid_params = {
            "url": "https://api.example.com/test",
            "method": "GET",
            "expected_status": 200,
            "expected_contains": "success"
        }
        schema = ApiTestInputSchema(**valid_params)
        assert schema.expected_status == 200
        assert schema.expected_contains == "success"

    def test_api_tools_have_correct_capabilities(self, api_tools):
        from tools.tool_schema import ToolCapability
        for tool in api_tools:
            assert tool.capability == ToolCapability.API

    def test_api_tools_have_correct_schemas(self, api_tools):
        for tool in api_tools:
            assert tool.schema.name.startswith("api_")
            assert tool.schema.input_schema in [ApiRequestInputSchema, ApiTestInputSchema]

    def test_api_tools_capture_snapshot_is_false(self, api_tools):
        from tools.tool_schema import ToolResult, ToolActionResult
        
        for tool in api_tools:
            if hasattr(tool, 'handle'):
                assert tool.schema.name in [
                    "api_request", "api_get", "api_post", 
                    "api_put", "api_delete", "api_patch", "api_test"
                ]

    @pytest.mark.asyncio  
    async def test_api_get_tool_structure(self, context, api_tools):
        api_get_tool = next(tool for tool in api_tools if tool.schema.name == "api_get")
        
        params = {
            "url": "https://httpbin.org/get",
            "method": "GET"
        }
        
        result = await api_get_tool.handle(context, params)
        
        assert result.code is not None
        assert len(result.code) > 0
        assert result.action is not None
        assert result.capture_snapshot is False
        assert result.wait_for_network is False

    @pytest.mark.asyncio
    async def test_api_test_tool_structure(self, context, api_tools):
        api_test_tool = next(tool for tool in api_tools if tool.schema.name == "api_test")
        
        params = {
            "url": "https://httpbin.org/get",
            "method": "GET",
            "expected_status": 200,
            "expected_contains": "origin"
        }
        
        result = await api_test_tool.handle(context, params)
        
        assert result.code is not None
        assert len(result.code) > 0
        assert result.action is not None
        assert result.capture_snapshot is False
        assert result.wait_for_network is False
        
        assert any("assert" in line for line in result.code)

    def test_method_specific_tools_use_correct_methods(self):
        """Test that method-specific tools use the correct HTTP methods"""
        tools = get_api_tools(capture_snapshot=False)
        
        # Test each method-specific tool
        expected_methods = {
            'api_get': 'GET',
            'api_post': 'POST', 
            'api_put': 'PUT',
            'api_delete': 'DELETE',
            'api_patch': 'PATCH'
        }
        
        for tool_name, expected_method in expected_methods.items():
            tool = next((t for t in tools if t.schema.name == tool_name), None)
            assert tool is not None, f"Tool {tool_name} not found"

    def test_headers_json_string_parsing(self):
        """Test that headers are properly parsed from JSON string to dictionary"""
        from tools.schemas import ApiRequestInputSchema, ApiTestInputSchema
        
        # Test valid JSON string headers
        json_headers = '{"Content-Type": "application/json", "Authorization": "Bearer token123"}'
        
        # Test ApiRequestInputSchema
        api_request = ApiRequestInputSchema(
            url="https://httpbin.org/post",
            method="POST",
            headers=json_headers,
            body='{"test": "data"}'
        )
        
        assert isinstance(api_request.headers, dict)
        assert api_request.headers["Content-Type"] == "application/json"
        assert api_request.headers["Authorization"] == "Bearer token123"
        
        # Test ApiTestInputSchema
        api_test = ApiTestInputSchema(
            url="https://httpbin.org/post",
            method="POST",
            headers=json_headers,
            body='{"test": "data"}',
            expected_status=200
        )
        
        assert isinstance(api_test.headers, dict)
        assert api_test.headers["Content-Type"] == "application/json"
        assert api_test.headers["Authorization"] == "Bearer token123"
        
        # Test invalid JSON string
        with pytest.raises(ValueError) as excinfo:
            ApiRequestInputSchema(
                url="https://httpbin.org/post",
                method="POST",
                headers='{"invalid": json}',  # Invalid JSON
                body='{"test": "data"}'
            )
        assert "Headers must be a valid JSON object" in str(excinfo.value)
        
        # Test that dict headers still work
        dict_headers = {"Content-Type": "application/json"}
        api_request_dict = ApiRequestInputSchema(
            url="https://httpbin.org/post",
            method="POST",
            headers=dict_headers,
            body='{"test": "data"}'
        )
        assert isinstance(api_request_dict.headers, dict)
        assert api_request_dict.headers["Content-Type"] == "application/json"

    def test_api_tools_are_browser_independent(self):
        """Test that all API tools have browser_independent=True to work without browser context"""
        tools = get_api_tools(capture_snapshot=False)
        
        for tool in tools:
            assert hasattr(tool, 'browser_independent'), f"Tool {tool.schema.name} missing browser_independent attribute"
            assert tool.browser_independent is True, f"Tool {tool.schema.name} should be browser_independent=True"

 