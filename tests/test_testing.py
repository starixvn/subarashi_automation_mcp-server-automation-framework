import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import sys
from pathlib import Path

# Add the parent directory to the path so we can import from the main package
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.conftest import assert_text_content, assert_contains_text_content
from context import ServerContext
from config.settings import Config, get_default_config, config_to_settings
from tools.testing import get_testing_tools
from services.testing_service import TestingService
from services.base_service import ServiceResult


@pytest.mark.asyncio
async def test_browser_generate_test_basic():
    # Test basic test generation
    testing_tools = get_testing_tools(capture_snapshot=False)
    generate_test_tool = next(tool for tool in testing_tools if tool.schema.name == "browser_generate_test")
    
    # Mock service result
    mock_service_result = ServiceResult(
        success=True,
        message="Test code generated successfully",
        data={
            "url": "https://example.com",
            "title": "Example Domain",
            "test_code": """import { test, expect } from '@playwright/test';

test('Test for Example Domain', async ({ page }) => {
  await page.goto('https://example.com');
  await expect(page).toHaveTitle('Example Domain');
});"""
        }
    )
    
    # Create mock context
    mock_context = MagicMock()
    
    with patch.object(TestingService, 'generate_test', return_value=mock_service_result):
        result = await generate_test_tool.handle(mock_context, {})
        
        # Test ToolResult structure
        assert result.code == [
            "# Generate test code for current page",
            "# Creates Playwright test template",
        ]
        assert result.capture_snapshot is False
        assert result.wait_for_network is False
        assert result.action is not None
        
        # Test action execution
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert "Generated test:" in action_result.content[0]["text"]
        assert "import { test, expect } from '@playwright/test';" in action_result.content[0]["text"]
        assert "Example Domain" in action_result.content[0]["text"]


@pytest.mark.asyncio
async def test_browser_generate_test_with_complex_page():
    # Test test generation for complex page
    testing_tools = get_testing_tools(capture_snapshot=False)
    generate_test_tool = next(tool for tool in testing_tools if tool.schema.name == "browser_generate_test")
    
    # Mock service result
    mock_service_result = ServiceResult(
        success=True,
        message="Test code generated successfully",
        data={
            "url": "https://app.example.com/login",
            "title": "Login - Example App",
            "test_code": """import { test, expect } from '@playwright/test';

test('Test for Login - Example App', async ({ page }) => {
  await page.goto('https://app.example.com/login');
  await expect(page).toHaveTitle('Login - Example App');
});"""
        }
    )
    
    # Create mock context
    mock_context = MagicMock()
    
    with patch.object(TestingService, 'generate_test', return_value=mock_service_result):
        result = await generate_test_tool.handle(mock_context, {})
        
        # Test action execution
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert "Generated test:" in action_result.content[0]["text"]
        assert "Login - Example App" in action_result.content[0]["text"]
        assert "https://app.example.com/login" in action_result.content[0]["text"]


@pytest.mark.asyncio
async def test_browser_generate_test_error_handling():
    # Test error handling in test generation
    testing_tools = get_testing_tools(capture_snapshot=False)
    generate_test_tool = next(tool for tool in testing_tools if tool.schema.name == "browser_generate_test")
    
    # Mock service error result
    mock_service_result = ServiceResult(
        success=False,
        message="Failed to generate test: No page available",
        error="No page available"
    )
    
    # Create mock context
    mock_context = MagicMock()
    
    with patch.object(TestingService, 'generate_test', return_value=mock_service_result):
        result = await generate_test_tool.handle(mock_context, {})
        
        # Test action execution with error
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert "Failed to generate test: No page available" in action_result.content[0]["text"]


@pytest.mark.asyncio
async def test_browser_generate_test_with_special_characters():
    # Test test generation with special characters in title
    testing_tools = get_testing_tools(capture_snapshot=False)
    generate_test_tool = next(tool for tool in testing_tools if tool.schema.name == "browser_generate_test")
    
    # Mock service result
    mock_service_result = ServiceResult(
        success=True,
        message="Test code generated successfully",
        data={
            "url": "https://example.com/special",
            "title": "Special & \"Quoted\" Page",
            "test_code": """import { test, expect } from '@playwright/test';

test('Test for Special & "Quoted" Page', async ({ page }) => {
  await page.goto('https://example.com/special');
  await expect(page).toHaveTitle('Special & "Quoted" Page');
});"""
        }
    )
    
    # Create mock context
    mock_context = MagicMock()
    
    with patch.object(TestingService, 'generate_test', return_value=mock_service_result):
        result = await generate_test_tool.handle(mock_context, {})
        
        # Test action execution
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert "Generated test:" in action_result.content[0]["text"]
        assert "Special & \"Quoted\" Page" in action_result.content[0]["text"]


@pytest.mark.asyncio
async def test_browser_generate_test_empty_page():
    # Test test generation for empty page
    testing_tools = get_testing_tools(capture_snapshot=False)
    generate_test_tool = next(tool for tool in testing_tools if tool.schema.name == "browser_generate_test")
    
    # Mock service result
    mock_service_result = ServiceResult(
        success=True,
        message="Test code generated successfully",
        data={
            "url": "about:blank",
            "title": "",
            "test_code": """import { test, expect } from '@playwright/test';

test('Test for ', async ({ page }) => {
  await page.goto('about:blank');
  await expect(page).toHaveTitle('');
});"""
        }
    )
    
    # Create mock context
    mock_context = MagicMock()
    
    with patch.object(TestingService, 'generate_test', return_value=mock_service_result):
        result = await generate_test_tool.handle(mock_context, {})
        
        # Test action execution
        action_result = await result.action()
        assert action_result.content[0]["type"] == "text"
        assert "Generated test:" in action_result.content[0]["text"]
        assert "about:blank" in action_result.content[0]["text"]


@pytest.mark.asyncio
async def test_testing_capability_filtering():
    # Test that testing tools have proper capability filtering
    testing_tools = get_testing_tools(capture_snapshot=False)
    
    # Check that we have the expected testing tools
    tool_names = [tool.schema.name for tool in testing_tools]
    expected_tools = ["browser_generate_test"]
    
    for expected_tool in expected_tools:
        assert expected_tool in tool_names, f"Missing testing tool: {expected_tool}"
    
    # Check that all tools have TESTING capability
    from core.tool_schema import ToolCapability
    for tool in testing_tools:
        assert tool.capability == ToolCapability.TESTING


@pytest.mark.asyncio
async def test_testing_tools_capture_snapshot_parameter():
    # Test that testing tools respect capture_snapshot parameter
    tools_with_snapshot = get_testing_tools(capture_snapshot=True)
    tools_without_snapshot = get_testing_tools(capture_snapshot=False)
    
    # Find generate test tool in both sets
    generate_test_with_snapshot = next(tool for tool in tools_with_snapshot if tool.schema.name == "browser_generate_test")
    generate_test_without_snapshot = next(tool for tool in tools_without_snapshot if tool.schema.name == "browser_generate_test")
    
    # Create mock context and service result
    mock_context = MagicMock()
    mock_service_result = ServiceResult(
        success=True,
        message="Test code generated successfully",
        data={
            "url": "https://example.com",
            "title": "Example Domain",
            "test_code": "test code"
        }
    )
    
    with patch.object(TestingService, 'generate_test', return_value=mock_service_result):
        result_with_snapshot = await generate_test_with_snapshot.handle(mock_context, {})
        result_without_snapshot = await generate_test_without_snapshot.handle(mock_context, {})
        
        assert result_with_snapshot.capture_snapshot is True
        assert result_without_snapshot.capture_snapshot is False


@pytest.mark.asyncio
async def test_testing_tools_schema_validation():
    # Test that testing tools have proper schema validation
    testing_tools = get_testing_tools(capture_snapshot=False)
    
    for tool in testing_tools:
        assert tool.schema.name is not None
        assert tool.schema.title is not None
        assert tool.schema.description is not None
        assert tool.schema.input_schema is not None
        assert tool.schema.tool_type is not None
        assert tool.handle is not None
        assert tool.capability is not None
        
        # Test that testing tools have read-only type
        from core.tool_schema import ToolType
        assert tool.schema.tool_type == ToolType.READ_ONLY


@pytest.mark.asyncio
async def test_testing_tools_network_settings():
    # Test that testing tools have proper network settings
    testing_tools = get_testing_tools(capture_snapshot=False)
    
    for tool in testing_tools:
        mock_context = MagicMock()
        mock_service_result = ServiceResult(
            success=True,
            message="Test code generated successfully",
            data={
                "url": "https://example.com",
                "title": "Example Domain",
                "test_code": "test code"
            }
        )
        
        with patch.object(TestingService, 'generate_test', return_value=mock_service_result):
            result = await tool.handle(mock_context, {})
            
            # Testing operations shouldn't wait for network
            assert result.wait_for_network is False 