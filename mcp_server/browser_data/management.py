import logging
import json
from typing import List
from mcp import types
from mcp_server.core.mcp_setup import mcp, get_service_context

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@mcp.tool(
    name="clear_browser_data",
    description="Clear cookies, localStorage, and sessionStorage.",
)
async def clear_browser_data() -> List[types.TextContent]:
    """
    Clear cookies, localStorage, and sessionStorage.

    Returns:
        List of TextContent with confirmation message
    """
    try:
        context = await get_service_context()
        page = await context.playwright_manager.ensure_browser()
        logger.info("Clearing browser data")
        await page.context.clear_cookies()
        
        await page.evaluate("""() => {
            try {
                localStorage.clear();
                sessionStorage.clear();
                return true;
            } catch (e) {
                console.error('Error clearing storage:', e);
                return false;
            }
        }""")

        return [types.TextContent(
            type="text",
            text="Browser data cleared successfully (cookies, localStorage, sessionStorage)"
        )]
        
    except Exception as e:
        error_msg = f"Failed to clear browser data: {str(e)}"
        logger.error(error_msg)
        return [types.TextContent(
            type="text",
            text=error_msg
        )]


@mcp.tool(name="get_cookies", description="Get all cookies for the current page.")
async def get_cookies() -> List[types.TextContent]:
    """
    Get all cookies for the current page.

    Returns:
        List of TextContent with JSON string of cookies
    """
    try:
        context = await get_service_context()
        page = await context.playwright_manager.ensure_browser()
        logger.info("Getting cookies")

        cookies = await page.context.cookies()
        
        if not cookies:
            return [types.TextContent(
                type="text",
                text="No cookies found for the current page"
            )]
        
        cookies_json = json.dumps(cookies, indent=2, default=str)
        
        return [types.TextContent(
            type="text",
            text=f"Found {len(cookies)} cookies:\n{cookies_json}"
        )]
        
    except Exception as e:
        error_msg = f"Failed to get cookies: {str(e)}"
        logger.error(error_msg)
        return [types.TextContent(
            type="text",
            text=error_msg
        )] 