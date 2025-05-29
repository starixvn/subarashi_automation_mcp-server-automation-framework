import logging
from mcp import types
from mcp_server.core.mcp_setup import mcp, get_service_context
from mcp_server.config.settings import settings
from typing import List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@mcp.tool(name="browser_fill", description="Fill a form field with text.")
async def browser_fill(selector: str, text: str) -> List[types.TextContent]:
    """
    Fill a form field with text.

    Args:
        selector: CSS or XPath selector to find the form field
        text: Text to fill the form field with

    Returns:
        List of TextContent với fill confirmation
    """
    try:
        if not selector or not isinstance(selector, str):
            return [types.TextContent(
                type="text",
                text="Error: Selector must be a non-empty string"
            )]
        if not isinstance(text, str):
            return [types.TextContent(
                type="text",
                text="Error: Text must be a string"
            )]

        if not settings.validate_selector(selector):
            return [types.TextContent(
                type="text",
                text=f"Error: Selector exceeds maximum length of {settings.MAX_SELECTOR_LENGTH} characters"
            )]

        context = await get_service_context()
        page = await context.playwright_manager.ensure_browser()
        logger.info(f"Filling text in selector: {selector}")

        await page.fill(selector, text)
        
        return [types.TextContent(
            type="text",
            text=f"Successfully filled text in element with selector '{selector}'"
        )]
        
    except Exception as e:
        error_msg = f"Could not fill element: {str(e)}"
        logger.error(error_msg)
        return [types.TextContent(
            type="text",
            text=error_msg
        )]


@mcp.tool(
    name="browser_click",
    description="Click on an element matching the selector",
)
async def browser_click(selector: str) -> List[types.TextContent]:
    """
    Click on an element matching the selector.

    Args:
        selector: CSS or XPath selector to find the element

    Returns:
        List of TextContent với click confirmation
    """
    try:
        if not selector or not isinstance(selector, str):
            return [types.TextContent(
                type="text",
                text="Error: Selector must be a non-empty string"
            )]

        if not settings.validate_selector(selector):
            return [types.TextContent(
                type="text",
                text=f"Error: Selector exceeds maximum length of {settings.MAX_SELECTOR_LENGTH} characters"
            )]

        context = await get_service_context()
        page = await context.playwright_manager.ensure_browser()
        logger.info(f"Clicking element with selector: {selector}")

        await page.click(selector, timeout=settings.BROWSER_CLICK_TIMEOUT)
        
        return [types.TextContent(
            type="text",
            text=f"Successfully clicked element with selector '{selector}'"
        )]
        
    except Exception as e:
        error_msg = f"Could not click element: {str(e)}"
        logger.error(error_msg)
        return [types.TextContent(
            type="text",
            text=error_msg
        )]


@mcp.tool(name="browser_press_key", description="Press a key on the keyboard.")
async def browser_press_key(key: str) -> List[types.TextContent]:
    """
    Press a key on the keyboard.

    Args:
        key: Key to press (e.g., 'Enter', 'Tab', 'ArrowDown')

    Returns:
        List of TextContent với key press confirmation
    """
    try:
        if not key or not isinstance(key, str):
            return [types.TextContent(
                type="text",
                text="Error: Key must be a non-empty string"
            )]

        context = await get_service_context()
        page = await context.playwright_manager.ensure_browser()
        logger.info(f"Pressing key: {key}")

        await page.keyboard.press(key)
        
        return [types.TextContent(
            type="text",
            text=f"Successfully pressed key '{key}'"
        )]
        
    except Exception as e:
        error_msg = f"Error pressing key: {str(e)}"
        logger.error(error_msg)
        return [types.TextContent(
            type="text",
            text=error_msg
        )]


@mcp.tool(
    name="browser_find_by_xpath",
    description="Find elements using an XPath expression and return their count.",
)
async def browser_find_by_xpath(xpath: str) -> List[types.TextContent]:
    """
    Find elements using an XPath expression and return their count.

    Args:
        xpath: XPath expression to find elements

    Returns:
        List of TextContent với count of matching elements
    """
    try:
        if not xpath or not isinstance(xpath, str):
            return [types.TextContent(
                type="text",
                text="Error: XPath must be a non-empty string"
            )]

        if len(xpath) > settings.MAX_XPATH_LENGTH:
            return [types.TextContent(
                type="text",
                text=f"Error: XPath exceeds maximum length of {settings.MAX_XPATH_LENGTH} characters"
            )]

        if not xpath.startswith("//") and not xpath.startswith("xpath="):
            xpath = f"xpath={xpath}"

        context = await get_service_context()
        page = await context.playwright_manager.ensure_browser()
        logger.info(f"Finding elements with XPath: {xpath}")

        elements = await page.query_selector_all(xpath)
        count = len(elements)
        
        return [types.TextContent(
            type="text",
            text=f"Found {count} elements matching XPath '{xpath}'"
        )]
        
    except Exception as e:
        error_msg = f"Error finding elements: {str(e)}"
        logger.error(error_msg)
        return [types.TextContent(
            type="text",
            text=error_msg
        )]


@mcp.tool(
    name="clear_field",
    description="Clear the content of a specific input field using XPath.",
)
async def clear_field(xpath: str) -> List[types.TextContent]:
    """
    Clear the content of a specific input field using XPath.

    Args:
        xpath: XPath query to find the input field

    Returns:
        List of TextContent với confirmation message or error message
    """
    try:
        if not xpath or not isinstance(xpath, str):
            return [types.TextContent(
                type="text",
                text="Error: XPath must be a non-empty string"
            )]

        # Validate xpath length
        if len(xpath) > settings.MAX_XPATH_LENGTH:
            return [types.TextContent(
                type="text",
                text=f"Error: XPath exceeds maximum length of {settings.MAX_XPATH_LENGTH} characters"
            )]

        context = await get_service_context()
        page = await context.playwright_manager.ensure_browser()
        logger.info(f"Clearing content of input field with XPath: {xpath}")

        element = await page.query_selector(f"xpath={xpath}")
        if not element:
            return [types.TextContent(
                type="text",
                text=f"Error: No input field found with XPath: {xpath}"
            )]

        await element.fill("")
        
        return [types.TextContent(
            type="text",
            text=f"Successfully cleared content of input field with XPath: {xpath}"
        )]
        
    except Exception as e:
        error_msg = f"Failed to clear input field: {str(e)}"
        logger.error(error_msg)
        return [types.TextContent(
            type="text",
            text=error_msg
        )]
