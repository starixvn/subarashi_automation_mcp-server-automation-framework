import logging
from mcp import types
from mcp_server.core.mcp_setup import mcp, get_service_context
from mcp_server.config.settings import settings
from typing import List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@mcp.tool(name="browser_navigate", description="Navigate to a URL in the browser.")
async def browser_navigate(url: str) -> List[types.TextContent]:
    """
    Navigate to a URL in the browser.

    Args:
        url: The URL to navigate to

    Returns:
        List of TextContent với navigation result
    """
    try:
        if not url or not isinstance(url, str):
            return [types.TextContent(
                type="text",
                text="Error: URL must be a non-empty string"
            )]

        if not settings.validate_url(url):
            return [types.TextContent(
                type="text",
                text=f"Error: URL exceeds maximum length of {settings.MAX_URL_LENGTH} characters"
            )]

        if not url.startswith(('http://', 'https://')):
            url = f"https://{url}"

        context = await get_service_context()
        page = await context.playwright_manager.ensure_browser()
        logger.info(f"Navigating to {url}")

        await page.goto(
            url, 
            wait_until=settings.BROWSER_WAIT_UNTIL, 
            timeout=settings.BROWSER_NAVIGATION_TIMEOUT
        )
        await page.wait_for_load_state("load", timeout=settings.BROWSER_LOAD_STATE_TIMEOUT)
        
        current_url = page.url
        title = await page.title()
        
        return [types.TextContent(
            type="text",
            text=f"Successfully navigated to {current_url}. Page title: {title}"
        )]

    except Exception as e:
        logger.error(f"Error navigating to {url}: {str(e)}")
        return [types.TextContent(
            type="text",
            text=f"Error navigating to {url}: {str(e)}"
        )]


@mcp.tool(name="browser_close", description="Close all browser resources explicitly.")
async def browser_close() -> List[types.TextContent]:
    """
    Close all browser resources explicitly.

    Returns:
        List of TextContent với closure confirmation
    """
    try:
        context = await get_service_context()
        await context.playwright_manager.close()
        
        return [types.TextContent(
            type="text",
            text="Browser closed successfully"
        )]
    except Exception as e:
        logger.error(f"Error closing browser: {str(e)}")
        return [types.TextContent(
            type="text",
            text=f"Error closing browser: {str(e)}"
        )]


@mcp.tool(
    name="browser_go_back", 
    description="Go back to the previous page in the browser."
)
async def browser_go_back() -> List[types.TextContent]:
    """
    Go back to the previous page in the browser.

    Returns:
        List of TextContent với navigation result
    """
    try:
        context = await get_service_context()
        page = await context.playwright_manager.ensure_browser()
        logger.info("Navigating back")

        await page.go_back(wait_until=settings.BROWSER_WAIT_UNTIL)
        current_url = page.url
        
        return [types.TextContent(
            type="text",
            text=f"Navigated back successfully. Current URL: {current_url}"
        )]
    except Exception as e:
        logger.error(f"Error navigating back: {str(e)}")
        return [types.TextContent(
            type="text",
            text=f"Error navigating back: {str(e)}"
        )]


@mcp.tool(name="browser_reload", description="Reload the current page.")
async def browser_reload() -> List[types.TextContent]:
    """
    Reload the current page.

    Returns:
        List of TextContent với reload confirmation
    """
    try:
        context = await get_service_context()
        page = await context.playwright_manager.ensure_browser()
        logger.info("Reloading page")

        await page.reload(wait_until=settings.BROWSER_WAIT_UNTIL)
        current_url = page.url
        
        return [types.TextContent(
            type="text",
            text=f"Page reloaded successfully. Current URL: {current_url}"
        )]
    except Exception as e:
        logger.error(f"Error reloading page: {str(e)}")
        return [types.TextContent(
            type="text",
            text=f"Error reloading page: {str(e)}"
        )]


@mcp.tool(name="get_current_url", description="Get the URL of the current page.")
async def get_current_url() -> List[types.TextContent]:
    """
    Get the URL of the current page.

    Returns:
        List of TextContent với current URL
    """
    try:
        context = await get_service_context()
        page = await context.playwright_manager.ensure_browser()
        url = page.url
        title = await page.title()

        return [types.TextContent(
            type="text",
            text=f"Current URL: {url}\nPage Title: {title}"
        )]
    except Exception as e:
        logger.error(f"Error getting current URL: {str(e)}")
        return [types.TextContent(
            type="text",
            text=f"Error getting current URL: {str(e)}"
        )]
