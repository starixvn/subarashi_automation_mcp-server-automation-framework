import logging
import asyncio
from mcp_tools.server.core.mcp_setup import mcp, pw_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@mcp.tool(name="Browser-Scroll-To-Top", description="Scroll the page to the very top.")
async def browser_scroll_to_top() -> str:
    """
    Scroll the page to the very top.

    Returns:
        Scroll confirmation
    """
    page = await pw_manager.ensure_browser()
    logger.info("Scrolling to top of page")

    try:
        # Use smooth scrolling for better user experience
        await page.evaluate(
            """() => {
            window.scrollTo({
                top: 0,
                left: 0,
                behavior: 'smooth'
            });
        }"""
        )
        await asyncio.sleep(0.5)
        return "Scrolled to top of page"
    except Exception as e:
        error_msg = f"Failed to scroll to top: {str(e)}"
        logger.error(error_msg)
        return error_msg


@mcp.tool(
    name="Browser-Scroll-To-Bottom", description="Scroll the page to the very bottom."
)
async def browser_scroll_to_bottom() -> str:
    """
    Scroll the page to the very bottom.

    Returns:
        Scroll confirmation
    """
    page = await pw_manager.ensure_browser()
    logger.info("Scrolling to bottom of page")

    try:
        # Calculate document height and scroll to it
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

        # Small wait to allow smooth scrolling to complete
        await asyncio.sleep(0.5)
        return "Scrolled to bottom of page"
    except Exception as e:
        error_msg = f"Failed to scroll to bottom: {str(e)}"
        logger.error(error_msg)
        return error_msg


@mcp.tool(
    name="Browser-Scroll-To-Element",
    description="Scroll the page until the specified element is in view.",
)
async def browser_scroll_to_element(selector: str) -> str:
    """
    Scroll the page until the specified element is in view.

    Args:
        selector: CSS or XPath selector for the element to scroll to

    Returns:
        Scroll confirmation
    """
    if not selector or not isinstance(selector, str):
        return "Error: Selector must be a non-empty string"

    page = await pw_manager.ensure_browser()
    logger.info(f"Scrolling to element with selector: {selector}")

    try:
        # First check if the element exists
        element = await page.query_selector(selector)
        if not element:
            return f"Error: No element found with selector: {selector}"

        # Scroll element into view with smooth behavior
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

        # Small wait to allow smooth scrolling to complete
        await asyncio.sleep(0.5)
        return f"Scrolled to element with selector '{selector}'"
    except Exception as e:
        error_msg = f"Failed to scroll to element: {str(e)}"
        logger.error(error_msg)
        return error_msg


@mcp.tool(name="Browser-Scroll-One-Step", description="Scroll the page by one step.")
async def browser_scroll_one_step(step: int = 100) -> str:
    """
    Scroll the page by one step.

    Args:
        step: The number of pixels to scroll. Positive for down, negative for up.

    Returns:
        Scroll confirmation message.
    """
    if not isinstance(step, int):
        return "Error: Step must be an integer"

    page = await pw_manager.ensure_browser()
    logger.info(f"Scrolling the page by {step} pixels")

    try:
        await page.evaluate(f"window.scrollBy(0, {step})")
        return f"Scrolled the page by {step} pixels"
    except Exception as e:
        error_msg = f"Failed to scroll the page: {str(e)}"
        logger.error(error_msg)
        return error_msg
