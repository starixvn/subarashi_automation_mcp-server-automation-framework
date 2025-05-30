import logging
from typing import List
from mcp import types
from mcp_server.core.mcp_setup import mcp, get_service_context
from mcp_server.config.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@mcp.tool(
    name="get_page_content",
    description="Get the visible text content of the current page.",
)
async def get_page_content() -> List[types.TextContent]:
    """
    Get the visible text content of the current page.

    Returns:
        List of TextContent with page text content
    """
    try:
        context = await get_service_context()
        page = await context.playwright_manager.ensure_browser()
        logger.info("Getting page content")

        content = await page.evaluate("""() => {
            return document.body.innerText || document.body.textContent || '';
        }""")
        
        if not content.strip():
            return [types.TextContent(
                type="text",
                text="No visible text content found on the current page"
            )]
        
        content_preview = content[:500] + "..." if len(content) > 500 else content
        
        return [types.TextContent(
            type="text",
            text=f"Page Content ({len(content)} characters):\n{content_preview}\n\nFull content: {content}"
        )]
        
    except Exception as e:
        error_msg = f"Failed to get page content: {str(e)}"
        logger.error(error_msg)
        return [types.TextContent(
            type="text",
            text=error_msg
        )]


@mcp.tool(
    name="get_page_html",
    description="Get the full HTML source of the current page.",
)
async def get_page_html() -> List[types.TextContent]:
    """
    Get the full HTML source of the current page.

    Returns:
        List of TextContent with page HTML source
    """
    try:
        context = await get_service_context()
        page = await context.playwright_manager.ensure_browser()
        logger.info("Getting page HTML")

        html = await page.content()
        
        if not html.strip():
            return [types.TextContent(
                type="text",
                text="No HTML content found on the current page"
            )]
        
        html_preview = html[:1000] + "..." if len(html) > 1000 else html
        
        return [types.TextContent(
            type="text",
            text=f"Page HTML ({len(html)} characters):\n{html_preview}\n\nFull HTML: {html}"
        )]
        
    except Exception as e:
        error_msg = f"Failed to get page HTML: {str(e)}"
        logger.error(error_msg)
        return [types.TextContent(
            type="text",
            text=error_msg
        )]


@mcp.tool(
    name="get_page_title",
    description="Get the title of the current page.",
)
async def get_page_title() -> List[types.TextContent]:
    """
    Get the title of the current page.

    Returns:
        List of TextContent with page title
    """
    try:
        context = await get_service_context()
        page = await context.playwright_manager.ensure_browser()
        logger.info("Getting page title")

        title = await page.title()
        url = page.url
        
        if not title.strip():
            return [types.TextContent(
                type="text",
                text=f"No title found for the current page. URL: {url}"
            )]
        
        return [types.TextContent(
            type="text",
            text=f"Page Title: {title}\nURL: {url}"
        )]
        
    except Exception as e:
        error_msg = f"Failed to get page title: {str(e)}"
        logger.error(error_msg)
        return [types.TextContent(
            type="text",
            text=error_msg
        )] 