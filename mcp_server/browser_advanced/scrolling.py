import logging
from typing import List
from mcp import types
from mcp_server.core.mcp_setup import mcp, get_service_context
from mcp_server.config.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@mcp.tool(
    name="browser_scroll_to_top",
    description="Scroll to the top of the page.",
)
async def browser_scroll_to_top() -> List[types.TextContent]:
    """
    Scroll to the top of the page.

    Returns:
        List of TextContent with scroll confirmation
    """
    try:
        context = await get_service_context()
        page = await context.playwright_manager.ensure_browser()
        logger.info("Scrolling to top of page")

        await page.evaluate("window.scrollTo(0, 0)")
        
        return [types.TextContent(
            type="text",
            text="Successfully scrolled to the top of the page"
        )]
        
    except Exception as e:
        error_msg = f"Failed to scroll to top: {str(e)}"
        logger.error(error_msg)
        return [types.TextContent(
            type="text",
            text=error_msg
        )]


@mcp.tool(
    name="browser_scroll_to_bottom",
    description="Scroll to the bottom of the page.",
)
async def browser_scroll_to_bottom() -> List[types.TextContent]:
    """
    Scroll to the bottom of the page.

    Returns:
        List of TextContent with scroll confirmation
    """
    try:
        context = await get_service_context()
        page = await context.playwright_manager.ensure_browser()
        logger.info("Scrolling to bottom of page")

        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        
        return [types.TextContent(
            type="text",
            text="Successfully scrolled to the bottom of the page"
        )]
        
    except Exception as e:
        error_msg = f"Failed to scroll to bottom: {str(e)}"
        logger.error(error_msg)
        return [types.TextContent(
            type="text",
            text=error_msg
        )]


@mcp.tool(
    name="browser_scroll_to_element",
    description="Scroll to a specific element on the page.",
)
async def browser_scroll_to_element(selector: str) -> List[types.TextContent]:
    """
    Scroll to a specific element on the page.

    Args:
        selector: CSS or XPath selector to find the element

    Returns:
        List of TextContent with scroll confirmation
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
        logger.info(f"Scrolling to element: {selector}")

        element = await page.query_selector(selector)
        if not element:
            return [types.TextContent(
                type="text",
                text=f"Error: Element not found with selector '{selector}'"
            )]

        await element.scroll_into_view_if_needed()
        
        return [types.TextContent(
            type="text",
            text=f"Successfully scrolled to element with selector '{selector}'"
        )]
        
    except Exception as e:
        error_msg = f"Failed to scroll to element: {str(e)}"
        logger.error(error_msg)
        return [types.TextContent(
            type="text",
            text=error_msg
        )]


@mcp.tool(
    name="browser_scroll_one_step",
    description="Scroll the page by one step in the specified direction.",
)
async def browser_scroll_one_step(direction: str = "down") -> List[types.TextContent]:
    """
    Scroll the page by one step in the specified direction.

    Args:
        direction: Direction to scroll ('up', 'down', 'left', 'right')

    Returns:
        List of TextContent with scroll confirmation
    """
    try:
        if direction not in ["up", "down", "left", "right"]:
            return [types.TextContent(
                type="text",
                text="Error: Direction must be 'up', 'down', 'left', or 'right'"
            )]

        context = await get_service_context()
        page = await context.playwright_manager.ensure_browser()
        logger.info(f"Scrolling one step {direction}")

        scroll_amount = 200  # pixels
        
        if direction == "down":
            await page.evaluate(f"window.scrollBy(0, {scroll_amount})")
        elif direction == "up":
            await page.evaluate(f"window.scrollBy(0, -{scroll_amount})")
        elif direction == "right":
            await page.evaluate(f"window.scrollBy({scroll_amount}, 0)")
        elif direction == "left":
            await page.evaluate(f"window.scrollBy(-{scroll_amount}, 0)")
        
        return [types.TextContent(
            type="text",
            text=f"Successfully scrolled {scroll_amount} pixels {direction}"
        )]
        
    except Exception as e:
        error_msg = f"Failed to scroll {direction}: {str(e)}"
        logger.error(error_msg)
        return [types.TextContent(
            type="text",
            text=error_msg
        )] 