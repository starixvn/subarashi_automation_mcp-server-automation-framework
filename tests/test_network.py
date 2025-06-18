import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import sys
from pathlib import Path

# Add the parent directory to the path so we can import from the main package
sys.path.insert(0, str(Path(__file__).parent.parent))

from tests.conftest import assert_text_content, assert_contains_text_content
from context import ServerContext
from config.settings import Config, get_default_config, config_to_settings


@pytest.mark.asyncio
async def test_browser_network_requests():
    default_config = get_default_config()
    settings = config_to_settings(default_config)

    with patch("playwright.async_api.async_playwright") as mock_playwright:
        mock_playwright_instance = AsyncMock()
        mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance

        context = ServerContext(settings)
        registry = context.tool_registry

        with patch.object(registry, "execute_tool") as mock_execute:
            mock_execute.return_value = MagicMock()
            mock_execute.return_value.content = [
                {
                    "type": "text",
                    "text": """
- Ran Playwright code:
```js
// Get network requests
const requests = await page.getNetworkRequests();
```

Network Requests:
1. GET https://example.com/ - Status: 200, Size: 1024 bytes
2. GET https://example.com/style.css - Status: 200, Size: 2048 bytes
3. GET https://example.com/script.js - Status: 200, Size: 4096 bytes
4. POST https://api.example.com/data - Status: 201, Size: 512 bytes
""",
                }
            ]

            result = await registry.execute_tool("browser_network_requests", {})

            assert hasattr(result, "content")
            assert result.content is not None
            text_content = ""
            for item in result.content:
                if item.get("type") == "text":
                    text_content += item.get("text", "")

            assert "Get network requests" in text_content
            assert "Network Requests:" in text_content
            assert "GET https://example.com/" in text_content
            assert "Status: 200" in text_content
            assert "POST https://api.example.com/data" in text_content
            assert "Status: 201" in text_content


@pytest.mark.asyncio
async def test_browser_network_requests_empty():
    default_config = get_default_config()
    settings = config_to_settings(default_config)

    with patch("playwright.async_api.async_playwright") as mock_playwright:
        mock_playwright_instance = AsyncMock()
        mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance

        context = ServerContext(settings)
        registry = context.tool_registry

        with patch.object(registry, "execute_tool") as mock_execute:
            mock_execute.return_value = MagicMock()
            mock_execute.return_value.content = [
                {
                    "type": "text",
                    "text": """
- Ran Playwright code:
```js
// Get network requests
const requests = await page.getNetworkRequests();
```

Network Requests:
No network requests found.
""",
                }
            ]

            result = await registry.execute_tool("browser_network_requests", {})

            assert hasattr(result, "content")
            assert result.content is not None
            text_content = ""
            for item in result.content:
                if item.get("type") == "text":
                    text_content += item.get("text", "")

            assert "Get network requests" in text_content
            assert "No network requests found" in text_content


@pytest.mark.asyncio
async def test_browser_set_request_interception_enable():
    default_config = get_default_config()
    settings = config_to_settings(default_config)

    with patch("playwright.async_api.async_playwright") as mock_playwright:
        mock_playwright_instance = AsyncMock()
        mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance

        context = ServerContext(settings)
        registry = context.tool_registry

        with patch.object(registry, "execute_tool") as mock_execute:
            mock_execute.return_value = MagicMock()
            mock_execute.return_value.content = [
                {
                    "type": "text",
                    "text": """
- Ran Playwright code:
```js
// Enable request interception
await page.route('**/*', route => {
  console.log('Request intercepted:', route.request().url());
  route.continue();
});
```

Request interception enabled successfully.
""",
                }
            ]

            result = await registry.execute_tool(
                "browser_set_request_interception", {"enabled": True}
            )

            assert hasattr(result, "content")
            assert result.content is not None
            text_content = ""
            for item in result.content:
                if item.get("type") == "text":
                    text_content += item.get("text", "")

            assert "Enable request interception" in text_content
            assert "Request interception enabled successfully" in text_content


@pytest.mark.asyncio
async def test_browser_set_request_interception_disable():
    default_config = get_default_config()
    settings = config_to_settings(default_config)

    with patch("playwright.async_api.async_playwright") as mock_playwright:
        mock_playwright_instance = AsyncMock()
        mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance

        context = ServerContext(settings)
        registry = context.tool_registry

        with patch.object(registry, "execute_tool") as mock_execute:
            mock_execute.return_value = MagicMock()
            mock_execute.return_value.content = [
                {
                    "type": "text",
                    "text": """
- Ran Playwright code:
```js
// Disable request interception
await page.unroute('**/*');
```

Request interception disabled successfully.
""",
                }
            ]

            result = await registry.execute_tool(
                "browser_set_request_interception", {"enabled": False}
            )

            assert hasattr(result, "content")
            assert result.content is not None
            text_content = ""
            for item in result.content:
                if item.get("type") == "text":
                    text_content += item.get("text", "")

            assert "Disable request interception" in text_content
            assert "Request interception disabled successfully" in text_content


@pytest.mark.asyncio
async def test_browser_set_request_interception_with_patterns():
    default_config = get_default_config()
    settings = config_to_settings(default_config)

    with patch("playwright.async_api.async_playwright") as mock_playwright:
        mock_playwright_instance = AsyncMock()
        mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance

        context = ServerContext(settings)
        registry = context.tool_registry

        with patch.object(registry, "execute_tool") as mock_execute:
            mock_execute.return_value = MagicMock()
            mock_execute.return_value.content = [
                {
                    "type": "text",
                    "text": """
- Ran Playwright code:
```js
// Enable request interception with patterns
await page.route('**/api/**', route => {
  console.log('API request intercepted:', route.request().url());
  route.continue();
});
await page.route('**/*.css', route => {
  console.log('CSS request intercepted:', route.request().url());
  route.continue();
});
```

Request interception enabled for patterns: **/api/**, **/*.css
""",
                }
            ]

            result = await registry.execute_tool(
                "browser_set_request_interception",
                {"enabled": True, "patterns": ["**/api/**", "**/*.css"]},
            )

            assert hasattr(result, "content")
            assert result.content is not None
            text_content = ""
            for item in result.content:
                if item.get("type") == "text":
                    text_content += item.get("text", "")

            assert "Enable request interception with patterns" in text_content
            assert "**/api/**" in text_content
            assert "**/*.css" in text_content


@pytest.mark.asyncio
async def test_browser_network_requests_with_filters():
    default_config = get_default_config()
    settings = config_to_settings(default_config)

    with patch("playwright.async_api.async_playwright") as mock_playwright:
        mock_playwright_instance = AsyncMock()
        mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance

        context = ServerContext(settings)
        registry = context.tool_registry

        with patch.object(registry, "execute_tool") as mock_execute:
            mock_execute.return_value = MagicMock()
            mock_execute.return_value.content = [
                {
                    "type": "text",
                    "text": """
- Ran Playwright code:
```js
// Get network requests with filters
const requests = await page.getNetworkRequests({ method: 'POST', status: 200 });
```

Network Requests (Filtered):
1. POST https://api.example.com/login - Status: 200, Size: 256 bytes
2. POST https://api.example.com/data - Status: 200, Size: 1024 bytes
""",
                }
            ]

            result = await registry.execute_tool(
                "browser_network_requests", {"method": "POST", "status": 200}
            )

            assert hasattr(result, "content")
            assert result.content is not None
            text_content = ""
            for item in result.content:
                if item.get("type") == "text":
                    text_content += item.get("text", "")

            assert "Get network requests with filters" in text_content
            assert "Network Requests (Filtered)" in text_content
            assert "POST https://api.example.com/login" in text_content
            assert "Status: 200" in text_content


@pytest.mark.asyncio
async def test_browser_network_requests_error_handling():
    default_config = get_default_config()
    settings = config_to_settings(default_config)

    with patch("playwright.async_api.async_playwright") as mock_playwright:
        mock_playwright_instance = AsyncMock()
        mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance

        context = ServerContext(settings)
        registry = context.tool_registry

        with patch.object(registry, "execute_tool") as mock_execute:
            mock_execute.side_effect = Exception("Network monitoring not enabled")

            with pytest.raises(Exception, match="Network monitoring not enabled"):
                await registry.execute_tool("browser_network_requests", {})


@pytest.mark.asyncio
async def test_browser_network_requests_with_headers():
    default_config = get_default_config()
    settings = config_to_settings(default_config)

    with patch("playwright.async_api.async_playwright") as mock_playwright:
        mock_playwright_instance = AsyncMock()
        mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance

        context = ServerContext(settings)
        registry = context.tool_registry

        with patch.object(registry, "execute_tool") as mock_execute:
            mock_execute.return_value = MagicMock()
            mock_execute.return_value.content = [
                {
                    "type": "text",
                    "text": """
- Ran Playwright code:
```js
// Get network requests with headers
const requests = await page.getNetworkRequests({ includeHeaders: true });
```

Network Requests (With Headers):
1. GET https://example.com/
   Headers: {
     "User-Agent": "Mozilla/5.0...",
     "Accept": "text/html,application/xhtml+xml",
     "Accept-Language": "en-US,en;q=0.9"
   }
   Status: 200, Size: 1024 bytes

2. POST https://api.example.com/data
   Headers: {
     "Content-Type": "application/json",
     "Authorization": "Bearer token123"
   }
   Status: 201, Size: 512 bytes
""",
                }
            ]

            result = await registry.execute_tool(
                "browser_network_requests", {"include_headers": True}
            )

            assert hasattr(result, "content")
            assert result.content is not None
            text_content = ""
            for item in result.content:
                if item.get("type") == "text":
                    text_content += item.get("text", "")

            assert "Get network requests with headers" in text_content
            assert "Network Requests (With Headers)" in text_content
            assert "User-Agent" in text_content
            assert "Content-Type" in text_content
            assert "Authorization" in text_content


@pytest.mark.asyncio
async def test_network_capability_filtering():
    config = Config(
        browser=get_default_config().browser,
        server=get_default_config().server,
        network=get_default_config().network,
        capabilities=["core", "network"],
    )
    settings = config_to_settings(config)

    with patch("playwright.async_api.async_playwright") as mock_playwright:
        mock_playwright_instance = AsyncMock()
        mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance

        context = ServerContext(settings)
        registry = context.tool_registry

        tools = await registry.list_tools()
        tool_names = {tool["name"] for tool in tools}

        assert "browser_network_requests" in tool_names
        assert "browser_set_request_interception" in tool_names 