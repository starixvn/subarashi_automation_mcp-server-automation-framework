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
async def test_browser_generate_test_basic():
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
// Generate test code for current page state
const generator = new TestGenerator(page);
const testCode = await generator.generateTest();
```

Generated Test Code:
```javascript
const { test, expect } = require('@playwright/test');

test('page interaction test', async ({ page }) => {
  await page.goto('https://example.com');
  await page.click('button[data-testid="submit"]');
  await page.fill('input[name="email"]', 'test@example.com');
  await expect(page.locator('.success-message')).toBeVisible();
});
```

Test saved to: test_generated.spec.js
""",
                }
            ]

            result = await registry.execute_tool("browser_generate_test", {})

            assert hasattr(result, "content")
            assert result.content is not None
            text_content = ""
            for item in result.content:
                if item.get("type") == "text":
                    text_content += item.get("text", "")

            assert "Generate test code for current page state" in text_content
            assert "Generated Test Code:" in text_content
            assert "const { test, expect } = require('@playwright/test');" in text_content
            assert "await page.goto('https://example.com');" in text_content
            assert "Test saved to: test_generated.spec.js" in text_content


@pytest.mark.asyncio
async def test_browser_generate_test_with_assertions():
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
// Generate test code with assertions
const generator = new TestGenerator(page, { includeAssertions: true });
const testCode = await generator.generateTest();
```

Generated Test Code with Assertions:
```javascript
const { test, expect } = require('@playwright/test');

test('form submission with validation', async ({ page }) => {
  await page.goto('https://form.example.com');
  
  // Check initial state
  await expect(page.locator('h1')).toHaveText('Contact Form');
  await expect(page.locator('#submit-btn')).toBeDisabled();
  
  // Fill form
  await page.fill('input[name="name"]', 'John Doe');
  await page.fill('input[name="email"]', 'john@example.com');
  await page.fill('textarea[name="message"]', 'Hello world');
  
  // Verify button is now enabled
  await expect(page.locator('#submit-btn')).toBeEnabled();
  
  // Submit form
  await page.click('#submit-btn');
  
  // Verify success
  await expect(page.locator('.success-alert')).toBeVisible();
  await expect(page.locator('.success-alert')).toHaveText('Message sent successfully!');
});
```

Test features:
- State verification
- Form interaction
- Validation checks
- Success confirmation

Test saved to: form_test.spec.js
""",
                }
            ]

            result = await registry.execute_tool(
                "browser_generate_test", {"include_assertions": True}
            )

            assert hasattr(result, "content")
            assert result.content is not None
            text_content = ""
            for item in result.content:
                if item.get("type") == "text":
                    text_content += item.get("text", "")

            assert "Generate test code with assertions" in text_content
            assert "Generated Test Code with Assertions:" in text_content
            assert "await expect(page.locator('h1')).toHaveText('Contact Form');" in text_content
            assert "State verification" in text_content
            assert "Form interaction" in text_content
            assert "Validation checks" in text_content


@pytest.mark.asyncio
async def test_browser_generate_test_custom_filename():
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
// Generate test code with custom filename
const generator = new TestGenerator(page);
const testCode = await generator.generateTest({ filename: 'login_flow.spec.js' });
```

Generated Test Code:
```javascript
const { test, expect } = require('@playwright/test');

test('login flow test', async ({ page }) => {
  await page.goto('https://app.example.com/login');
  await page.fill('#username', 'testuser');
  await page.fill('#password', 'secret123');
  await page.click('#login-btn');
  await expect(page).toHaveURL('https://app.example.com/dashboard');
});
```

Test saved to: login_flow.spec.js
""",
                }
            ]

            result = await registry.execute_tool(
                "browser_generate_test", {"filename": "login_flow.spec.js"}
            )

            assert hasattr(result, "content")
            assert result.content is not None
            text_content = ""
            for item in result.content:
                if item.get("type") == "text":
                    text_content += item.get("text", "")

            assert "Generate test code with custom filename" in text_content
            assert "Test saved to: login_flow.spec.js" in text_content
            assert "test('login flow test'" in text_content


@pytest.mark.asyncio
async def test_browser_generate_test_multiple_languages():
    default_config = get_default_config()
    settings = config_to_settings(default_config)

    with patch("playwright.async_api.async_playwright") as mock_playwright:
        mock_playwright_instance = AsyncMock()
        mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance

        context = ServerContext(settings)
        registry = context.tool_registry

        def get_sample_code(language):
            if language == "javascript":
                return "const { test, expect } = require('@playwright/test');"
            elif language == "typescript":
                return "import { test, expect } from '@playwright/test';"
            elif language == "python":
                return "import pytest\nfrom playwright.sync_api import Page, expect"
            elif language == "java":
                return "import com.microsoft.playwright.*;"
            elif language == "csharp":
                return "using Microsoft.Playwright;"
            return ""

        def get_extension(language):
            extensions = {
                "javascript": "spec.js",
                "typescript": "spec.ts",
                "python": "test.py",
                "java": "java",
                "csharp": "cs",
            }
            return extensions.get(language, "txt")

        languages = ["javascript", "typescript", "python"]

        for language in languages:
            with patch.object(registry, "execute_tool") as mock_execute:
                mock_execute.return_value = MagicMock()
                mock_execute.return_value.content = [
                    {
                        "type": "text",
                        "text": f"""
- Ran Playwright code:
```js
// Generate test code in {language}
const generator = new TestGenerator(page, {{ language: '{language}' }});
const testCode = await generator.generateTest();
```

Generated {language.capitalize()} Test Code:
```{language}
{get_sample_code(language)}
```

Test saved to: test.{get_extension(language)}
""",
                    }
                ]

                result = await registry.execute_tool(
                    "browser_generate_test", {"language": language}
                )

                assert hasattr(result, "content")
                assert result.content is not None
                text_content = ""
                for item in result.content:
                    if item.get("type") == "text":
                        text_content += item.get("text", "")

                assert f"Generate test code in {language}" in text_content
                assert f"Generated {language.capitalize()} Test Code:" in text_content


@pytest.mark.asyncio
async def test_browser_generate_test_with_data_attributes():
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
// Generate test code prioritizing data attributes
const generator = new TestGenerator(page, { preferDataAttributes: true });
const testCode = await generator.generateTest();
```

Generated Test Code (Data Attribute Optimized):
```javascript
const { test, expect } = require('@playwright/test');

test('shopping cart test', async ({ page }) => {
  await page.goto('https://shop.example.com');
  
  // Use data-testid attributes for reliable selectors
  await page.click('[data-testid="add-to-cart-btn"]');
  await page.click('[data-testid="cart-icon"]');
  await expect(page.locator('[data-testid="cart-item"]')).toBeVisible();
  await page.click('[data-testid="checkout-btn"]');
  
  // Form interactions with data attributes
  await page.fill('[data-testid="email-input"]', 'customer@example.com');
  await page.fill('[data-testid="address-input"]', '123 Main St');
  await page.click('[data-testid="place-order-btn"]');
  
  await expect(page.locator('[data-testid="success-message"]')).toHaveText('Order placed successfully!');
});
```

Selector Strategy: Data attributes prioritized for stability
Test saved to: shopping_cart.spec.js
""",
                }
            ]

            result = await registry.execute_tool(
                "browser_generate_test", {"prefer_data_attributes": True}
            )

            assert hasattr(result, "content")
            assert result.content is not None
            text_content = ""
            for item in result.content:
                if item.get("type") == "text":
                    text_content += item.get("text", "")

            assert "Generate test code prioritizing data attributes" in text_content
            assert "Data Attribute Optimized" in text_content
            assert '[data-testid="add-to-cart-btn"]' in text_content
            assert "Selector Strategy: Data attributes prioritized" in text_content


@pytest.mark.asyncio
async def test_browser_generate_test_error_handling():
    default_config = get_default_config()
    settings = config_to_settings(default_config)

    with patch("playwright.async_api.async_playwright") as mock_playwright:
        mock_playwright_instance = AsyncMock()
        mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance

        context = ServerContext(settings)
        registry = context.tool_registry

        with patch.object(registry, "execute_tool") as mock_execute:
            mock_execute.side_effect = Exception("No interactions recorded on current page")

            with pytest.raises(Exception, match="No interactions recorded on current page"):
                await registry.execute_tool("browser_generate_test", {})


@pytest.mark.asyncio
async def test_testing_capability_filtering():
    config = Config(
        browser=get_default_config().browser,
        server=get_default_config().server,
        network=get_default_config().network,
        capabilities=["core", "testing"],
    )
    settings = config_to_settings(config)

    with patch("playwright.async_api.async_playwright") as mock_playwright:
        mock_playwright_instance = AsyncMock()
        mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance

        context = ServerContext(settings)
        registry = context.tool_registry

        tools = await registry.list_tools()
        tool_names = {tool["name"] for tool in tools}

        assert "browser_generate_test" in tool_names 