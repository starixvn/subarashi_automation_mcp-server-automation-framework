import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from tests.conftest import assert_text_content, assert_contains_text_content
from context import ServerContext
from tools.registry import EnhancedToolRegistry
from tools.tool_schema import ToolCapability
from config.settings import Config, get_default_config, config_to_settings


@pytest.mark.asyncio
async def test_snapshot_tool_list(tool_registry: EnhancedToolRegistry):
    tools = await tool_registry.list_tools()
    tool_names = {tool["name"] for tool in tools}

    expected_tools = {
        "browser_navigate",
        "browser_click",
        "browser_type",
        "browser_select_option",
        "browser_hover",
        "browser_close",
        "browser_resize",
        "browser_screenshot",
        "browser_capture_snapshot",
        "browser_screen_click",
        "browser_save_screenshot",
    }

    core_tools = {"browser_navigate", "browser_click", "browser_type", "browser_close"}
    for tool in core_tools:
        assert tool in tool_names, f"Core tool {tool} should be available"

    found_tools = expected_tools.intersection(tool_names)
    assert len(found_tools) >= len(
        core_tools
    ), f"Should have at least core tools, found: {tool_names}"


@pytest.mark.asyncio
async def test_vision_tool_list():
    config = Config(capabilities=["vision"])
    default_config = get_default_config()
    merged_config = Config(
        browser=default_config.browser,
        server=default_config.server,
        network=default_config.network,
        capabilities=config.capabilities,
    )
    settings = config_to_settings(merged_config)

    with patch("playwright.async_api.async_playwright") as mock_playwright:
        mock_playwright_instance = AsyncMock()
        mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance

        context = ServerContext(settings)
        registry = context.tool_registry

        tools = await registry.list_tools()
        tool_names = {tool["name"] for tool in tools}

        expected_vision_tools = {
            "browser_screen_click",
        }

        vision_tools_found = [
            tool for tool in expected_vision_tools if tool in tool_names
        ]
        screen_tools_found = [tool for tool in tool_names if "screen" in tool]

        assert (
            len(vision_tools_found) > 0 or len(screen_tools_found) > 0
        ), f"Should have some vision/screen tools, found: {tool_names}"


@pytest.mark.asyncio
async def test_core_capabilities():
    config = Config(capabilities=["core"])
    default_config = get_default_config()
    merged_config = Config(
        browser=default_config.browser,
        server=default_config.server,
        network=default_config.network,
        capabilities=config.capabilities,
    )
    settings = config_to_settings(merged_config)

    with patch("playwright.async_api.async_playwright") as mock_playwright:
        mock_playwright_instance = AsyncMock()
        mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance

        context = ServerContext(settings)
        registry = context.tool_registry

        tools = await registry.list_tools()
        tool_names = {tool["name"] for tool in tools}

        core_tools = {
            "browser_navigate",
            "browser_click",
            "browser_type",
        }

        for tool in core_tools:
            assert tool in tool_names, f"Core tool {tool} should be available"


@pytest.mark.asyncio
async def test_files_capabilities():
    config = Config(capabilities=["core", "files"])
    default_config = get_default_config()
    merged_config = Config(
        browser=default_config.browser,
        server=default_config.server,
        network=default_config.network,
        capabilities=config.capabilities,
    )
    settings = config_to_settings(merged_config)

    with patch("playwright.async_api.async_playwright") as mock_playwright:
        mock_playwright_instance = AsyncMock()
        mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance

        context = ServerContext(settings)
        registry = context.tool_registry

        tools = await registry.list_tools()
        tool_names = {tool["name"] for tool in tools}

        core_tools = {
            "browser_navigate",
            "browser_click",
            "browser_type",
        }

        for tool in core_tools:
            assert (
                tool in tool_names
            ), f"Core tool {tool} should be available with files capabilities"


@pytest.mark.asyncio
async def test_network_capabilities():
    config = Config(capabilities=["core", "network"])
    default_config = get_default_config()
    merged_config = Config(
        browser=default_config.browser,
        server=default_config.server,
        network=default_config.network,
        capabilities=config.capabilities,
    )
    settings = config_to_settings(merged_config)

    with patch("playwright.async_api.async_playwright") as mock_playwright:
        mock_playwright_instance = AsyncMock()
        mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance

        context = ServerContext(settings)
        registry = context.tool_registry

        tools = await registry.list_tools()
        tool_names = {tool["name"] for tool in tools}

        core_tools = {
            "browser_navigate",
            "browser_click",
            "browser_type",
        }

        for tool in core_tools:
            assert (
                tool in tool_names
            ), f"Core tool {tool} should be available with network capabilities"


@pytest.mark.asyncio
async def test_multiple_capabilities():
    config = Config(capabilities=["core", "vision"])
    default_config = get_default_config()
    merged_config = Config(
        browser=default_config.browser,
        server=default_config.server,
        network=default_config.network,
        capabilities=config.capabilities,
    )
    settings = config_to_settings(merged_config)

    with patch("playwright.async_api.async_playwright") as mock_playwright:
        mock_playwright_instance = AsyncMock()
        mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance

        context = ServerContext(settings)
        registry = context.tool_registry

        tools = await registry.list_tools()
        tool_names = {tool["name"] for tool in tools}

        expected_core_tools = {
            "browser_navigate",
            "browser_click",
            "browser_type",
        }

        for tool in expected_core_tools:
            assert (
                tool in tool_names
            ), f"Core tool {tool} should be available with multiple capabilities"


@pytest.mark.asyncio
async def test_capability_filtering():
    restricted_config = Config(capabilities=["core"])
    default_config = get_default_config()
    restricted_merged = Config(
        browser=default_config.browser,
        server=default_config.server,
        network=default_config.network,
        capabilities=restricted_config.capabilities,
    )
    restricted_settings = config_to_settings(restricted_merged)

    full_config = Config(capabilities=["core", "vision"])
    full_merged = Config(
        browser=default_config.browser,
        server=default_config.server,
        network=default_config.network,
        capabilities=full_config.capabilities,
    )
    full_settings = config_to_settings(full_merged)

    with patch("playwright.async_api.async_playwright") as mock_playwright:
        mock_playwright_instance = AsyncMock()
        mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance

        restricted_context = ServerContext(restricted_settings)
        restricted_registry = restricted_context.tool_registry

        full_context = ServerContext(full_settings)
        full_registry = full_context.tool_registry

        restricted_tools = await restricted_registry.list_tools()
        full_tools = await full_registry.list_tools()

        restricted_tool_names = {tool["name"] for tool in restricted_tools}
        full_tool_names = {tool["name"] for tool in full_tools}

        core_tools = {"browser_navigate", "browser_click", "browser_type"}

        for tool in core_tools:
            assert (
                tool in restricted_tool_names
            ), f"Restricted should have core tool {tool}"
            assert tool in full_tool_names, f"Full should have core tool {tool}"


@pytest.mark.asyncio
async def test_invalid_capability():
    config = Config(capabilities=["core", "invalid_capability"])
    default_config = get_default_config()
    merged_config = Config(
        browser=default_config.browser,
        server=default_config.server,
        network=default_config.network,
        capabilities=config.capabilities,
    )
    settings = config_to_settings(merged_config)

    with patch("playwright.async_api.async_playwright") as mock_playwright:
        mock_playwright_instance = AsyncMock()
        mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance

        context = ServerContext(settings)
        registry = context.tool_registry

        tools = await registry.list_tools()
        tool_names = {tool["name"] for tool in tools}

        core_tools = {"browser_navigate", "browser_click", "browser_type"}
        for tool in core_tools:
            assert (
                tool in tool_names
            ), f"Should have core tool {tool} despite invalid capability"


@pytest.mark.asyncio
async def test_empty_capabilities():
    config = Config(capabilities=[])
    default_config = get_default_config()
    merged_config = Config(
        browser=default_config.browser,
        server=default_config.server,
        network=default_config.network,
        capabilities=config.capabilities,
    )
    settings = config_to_settings(merged_config)

    with patch("playwright.async_api.async_playwright") as mock_playwright:
        mock_playwright_instance = AsyncMock()
        mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance

        context = ServerContext(settings)
        registry = context.tool_registry

        tools = await registry.list_tools()

        assert isinstance(tools, list), "Should return a list of tools"
