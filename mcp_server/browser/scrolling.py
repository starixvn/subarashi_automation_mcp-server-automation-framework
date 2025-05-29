import logging
import asyncio
from mcp import types
from mcp_server.core.mcp_setup import mcp, get_service_context
from mcp_server.config.settings import settings
from typing import List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@mcp.tool(name="browser_scroll_to_top", description="Scroll the page to the very top.")
async def browser_scroll_to_top() -> List[types.TextContent]:
    """
    Scroll the page to the very top.

    Returns:
        List of TextContent với scroll confirmation
    """
    try:
        context = await get_service_context()
        page = await context.playwright_manager.ensure_browser()
        logger.info("Scrolling to top of page")

        await page.evaluate(
            """() => {
            window.scrollTo({
                top: 0,
                left: 0,
                behavior: 'smooth'
            });
        }"""
        )
        await asyncio.sleep(settings.BROWSER_SCROLL_DELAY)
        
        return [types.TextContent(
            type="text",
            text="Successfully scrolled to top of page"
        )]
        
    except Exception as e:
        error_msg = f"Failed to scroll to top: {str(e)}"
        logger.error(error_msg)
        return [types.TextContent(
            type="text",
            text=error_msg
        )]


@mcp.tool(
    name="browser_scroll_to_bottom", description="Scroll the page to the very bottom."
)
async def browser_scroll_to_bottom() -> List[types.TextContent]:
    """
    Scroll the page to the very bottom.

    Returns:
        List of TextContent với scroll confirmation
    """
    try:
        context = await get_service_context()
        page = await context.playwright_manager.ensure_browser()
        logger.info("Scrolling to bottom of page")

        await page.evaluate(
            """() => {
            const scrollHeight = Math.max(
                document.body.scrollHeight,
                document.documentElement.scrollHeight,
                document.body.offsetHeight,
                document.documentElement.offsetHeight,
                document.body.clientHeight,
                document.documentElement.clientHeight
            );
            
            window.scrollTo({
                top: scrollHeight,
                left: 0,
                behavior: 'smooth'
            });
        }"""
        )

        await asyncio.sleep(settings.BROWSER_SCROLL_DELAY)
        
        return [types.TextContent(
            type="text",
            text="Successfully scrolled to bottom of page"
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
    description="Scroll the page until the specified element is in view.",
)
async def browser_scroll_to_element(selector: str) -> List[types.TextContent]:
    """
    Scroll the page until the specified element is in view.

    Args:
        selector: CSS or XPath selector for the element to scroll to

    Returns:
        List of TextContent với scroll confirmation
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
        logger.info(f"Scrolling to element with selector: {selector}")

        element = await page.query_selector(selector)
        if not element:
            return [types.TextContent(
                type="text",
                text=f"Error: No element found with selector: {selector}"
            )]

        await page.evaluate(
            f"""
            (selector) => {{
                const element = document.querySelector(selector);
                if (element) {{
                    element.scrollIntoView({{
                        behavior: 'smooth',
                        block: 'center'
                    }});
                }}
            }}
        """,
            selector,
        )

        await asyncio.sleep(settings.BROWSER_SCROLL_DELAY)
        
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


@mcp.tool(name="browser_scroll_one_step", description="Scroll the page by one step.")
async def browser_scroll_one_step(step: int = 100) -> List[types.TextContent]:
    """
    Scroll the page by one step.

    Args:
        step: The number of pixels to scroll. Positive for down, negative for up.

    Returns:
        List of TextContent với scroll confirmation message
    """
    try:
        if not isinstance(step, int):
            return [types.TextContent(
                type="text",
                text="Error: Step must be an integer"
            )]

        context = await get_service_context()
        page = await context.playwright_manager.ensure_browser()
        logger.info(f"Scrolling the page by {step} pixels")

        await page.evaluate(f"window.scrollBy(0, {step})")
        
        return [types.TextContent(
            type="text",
            text=f"Successfully scrolled the page by {step} pixels"
        )]
        
    except Exception as e:
        error_msg = f"Failed to scroll the page: {str(e)}"
        logger.error(error_msg)
        return [types.TextContent(
            type="text",
            text=error_msg
        )]
