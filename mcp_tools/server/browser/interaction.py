import logging
from mcp_tools.server.core.mcp_setup import mcp, pw_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@mcp.tool(name="Browser-Fill", description="Fill a form field with text.")
async def browser_fill(selector: str, text: str) -> str:
    """
    Fill a form field with text.

    Args:
        selector: CSS or XPath selector to find the form field
        text: Text to fill the form field with

    Returns:
        Fill confirmation
    """
    if not selector or not isinstance(selector, str):
        return "Error: Selector must be a non-empty string"
    if not isinstance(text, str):
        return "Error: Text must be a string"

    page = await pw_manager.ensure_browser()
    logger.info(f"Filling text in selector: {selector}")

    try:
        await page.fill(selector, text)
    except Exception as e:
        error_msg = f"Could not fill element: {str(e)}"
        logger.error(error_msg)
        return error_msg

    return f"Filled text in element with selector '{selector}'"


@mcp.tool(
    name="Browser-Click",
    description="Click on an element matching the selector",
)
async def browser_click(selector: str) -> str:
    """
    Click on an element matching the selector.

    Args:
        selector: CSS or XPath selector to find the element

    Returns:
        Click confirmation
    """
    if not selector or not isinstance(selector, str):
        return "Error: Selector must be a non-empty string"

    page = await pw_manager.ensure_browser()
    logger.info(f"Clicking element with selector: {selector}")

    try:
        await page.click(selector, timeout=5000)
    except Exception as e:
        error_msg = f"Could not click element: {str(e)}"
        logger.error(error_msg)
        return error_msg

    return f"Clicked element with selector '{selector}'"


@mcp.tool(name="Browser-Press-Key", description="Press a key on the keyboard.")
async def browser_press_key(key: str) -> str:
    """
    Press a key on the keyboard.

    Args:
        key: Key to press (e.g., 'Enter', 'Tab', 'ArrowDown')

    Returns:
        Key press confirmation
    """
    if not key or not isinstance(key, str):
        return "Error: Key must be a non-empty string"

    page = await pw_manager.ensure_browser()
    logger.info(f"Pressing key: {key}")

    try:
        await page.keyboard.press(key)
    except Exception as e:
        error_msg = f"Error pressing key: {str(e)}"
        logger.error(error_msg)
        return error_msg

    return f"Pressed key {key}"


@mcp.tool(
    name="Browser-Find-By-XPath",
    description="Find elements using an XPath expression and return their count.",
)
async def browser_find_by_xpath(xpath: str) -> str:
    """
    Find elements using an XPath expression and return their count.

    Args:
        xpath: XPath expression to find elements

    Returns:
        Count of matching elements
    """
    if not xpath or not isinstance(xpath, str):
        return "Error: XPath must be a non-empty string"

    # Ensure xpath is formatted properly
    if not xpath.startswith("//") and not xpath.startswith("xpath="):
        xpath = f"xpath={xpath}"

    page = await pw_manager.ensure_browser()
    logger.info(f"Finding elements with XPath: {xpath}")

    try:
        count = len(await page.query_selector_all(xpath))
        return f"Found {count} elements matching XPath '{xpath}'"
    except Exception as e:
        error_msg = f"Error finding elements: {str(e)}"
        logger.error(error_msg)
        return error_msg


@mcp.tool(
    name="Clear-Field",
    description="Clear the content of a specific input field using XPath.",
)
async def clear_field(xpath: str) -> str:
    """
    Clear the content of a specific input field using XPath.

    Args:
        xpath: XPath query to find the input field

    Returns:
        Confirmation message or error message
    """
    if not xpath or not isinstance(xpath, str):
        return "Error: XPath must be a non-empty string"

    page = await pw_manager.ensure_browser()
    logger.info(f"Clearing content of input field with XPath: {xpath}")

    try:
        element = await page.query_selector(f"xpath={xpath}")
        if not element:
            return f"Error: No input field found with XPath: {xpath}"

        await element.fill("")  # Clear the field by filling it with an empty string
        return f"Cleared content of input field with XPath: {xpath}"
    except Exception as e:
        error_msg = f"Failed to clear input field: {str(e)}"
        logger.error(error_msg)
        return error_msg
