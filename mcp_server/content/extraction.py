import logging
import os
from typing import Optional, List
from datetime import datetime
from mcp import types
from mcp_server.core.mcp_setup import mcp, get_service_context
from mcp_server.config.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@mcp.tool(
    name="get_element_html",
    description="Get the HTML content of a specific element using XPath.",
)
async def get_element_html(xpath: str) -> List[types.TextContent]:
    """
    Get the HTML content of a specific element using XPath.

    Args:
        xpath: XPath query to find the element

    Returns:
        List of TextContent với HTML content of the element or error message
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

        context = await get_service_context()
        page = await context.playwright_manager.ensure_browser()
        logger.info(f"Getting HTML content from element with XPath: {xpath}")

        element = await page.query_selector(f"xpath={xpath}")
        if not element:
            return [types.TextContent(
                type="text",
                text=f"Error: No element found with XPath: {xpath}"
            )]

        html_content = await element.inner_html()
        
        return [types.TextContent(
            type="text",
            text=html_content
        )]
        
    except Exception as e:
        error_msg = f"Error getting element HTML: {str(e)}"
        logger.error(error_msg)
        return [types.TextContent(
            type="text",
            text=error_msg
        )]


@mcp.tool(
    name="get_element_text",
    description="Get the text content of an element using XPath.",
)
async def get_element_text(xpath: str) -> List[types.TextContent]:
    """
    Get the text content of an element using XPath.

    Args:
        xpath: XPath query to find the element

    Returns:
        List of TextContent với text content of the element or error message
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

        context = await get_service_context()
        page = await context.playwright_manager.ensure_browser()
        logger.info(f"Getting text from element with XPath: {xpath}")

        element = await page.query_selector(f"xpath={xpath}")
        if not element:
            return [types.TextContent(
                type="text",
                text=f"Error: No element found with XPath: {xpath}"
            )]

        text = await element.inner_text()
        
        return [types.TextContent(
            type="text",
            text=text
        )]
        
    except Exception as e:
        error_msg = f"Error getting element text: {str(e)}"
        logger.error(error_msg)
        return [types.TextContent(
            type="text",
            text=error_msg
        )]


@mcp.tool(
    name="get_page_content", description="Get the text content of the current page."
)
async def get_page_content() -> List[types.TextContent]:
    """
    Get the text content of the current page.

    Returns:
        List of TextContent với text content of the page
    """
    try:
        context = await get_service_context()
        page = await context.playwright_manager.ensure_browser()
        
        text_content = await page.evaluate(
            """() => {
            return document.body.innerText;
        }"""
        )

        return [types.TextContent(
            type="text",
            text=text_content
        )]
        
    except Exception as e:
        error_msg = f"Error getting page content: {str(e)}"
        logger.error(error_msg)
        return [types.TextContent(
            type="text",
            text=error_msg
        )]


@mcp.tool(name="get_page_html", description="Get the HTML content of the current page.")
async def get_page_html() -> List[types.TextContent]:
    """
    Get the HTML content of the current page.

    Returns:
        List of TextContent với HTML content of the page
    """
    try:
        context = await get_service_context()
        page = await context.playwright_manager.ensure_browser()
        html_content = await page.content()

        return [types.TextContent(
            type="text",
            text=html_content
        )]
        
    except Exception as e:
        error_msg = f"Error getting page HTML: {str(e)}"
        logger.error(error_msg)
        return [types.TextContent(
            type="text",
            text=error_msg
        )]


@mcp.tool(name="get_page_title", description="Get the title of the current page.")
async def get_page_title() -> List[types.TextContent]:
    """
    Get the title of the current page.

    Returns:
        List of TextContent với page title
    """
    try:
        context = await get_service_context()
        page = await context.playwright_manager.ensure_browser()
        title = await page.title()

        return [types.TextContent(
            type="text",
            text=title
        )]
        
    except Exception as e:
        error_msg = f"Error getting page title: {str(e)}"
        logger.error(error_msg)
        return [types.TextContent(
            type="text",
            text=error_msg
        )]


@mcp.tool(
    name="save_element_as_html",
    description="Save a specific element's HTML content to a file using XPath.",
)
async def save_element_as_html(xpath: str, file_path: str = None) -> List[types.TextContent]:
    """
    Save a specific element's HTML content to a file using XPath.

    Args:
        xpath: XPath query to find the element
        file_path: Optional path to save the HTML file. If not provided, a default path will be used.

    Returns:
        List of TextContent với path to the saved HTML file
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

        context = await get_service_context()
        page = await context.playwright_manager.ensure_browser()
        logger.info(f"Saving HTML content of element with XPath: {xpath}")

        if not file_path:
            timestamp = datetime.now().strftime(settings.TIMESTAMP_FORMAT)
            filename = f"element_{timestamp}.html"
            file_path = settings.get_output_path(filename, "html")

        element = await page.query_selector(f"xpath={xpath}")
        if not element:
            return [types.TextContent(
                type="text",
                text=f"Error: No element found with XPath: {xpath}"
            )]

        html_content = await element.evaluate("(node) => node.outerHTML")
        if not html_content:
            return [types.TextContent(
                type="text",
                text=f"Error: Could not extract HTML from element with XPath: {xpath}"
            )]

        full_html = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset='utf-8'>
            <title>Extracted Element HTML</title>
        </head>
        <body>
            <!-- Element with XPath: {xpath} -->
            {html_content}
        </body>
        </html>"""

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(full_html)

        return [types.TextContent(
            type="text",
            text=f"Element HTML saved successfully to {file_path}"
        )]
        
    except Exception as e:
        error_msg = f"Failed to save element HTML: {str(e)}"
        logger.error(error_msg)
        return [types.TextContent(
            type="text",
            text=error_msg
        )]


@mcp.tool(
    name="save_page_as_html",
    description="Save the current page's HTML content to a file.",
)
async def save_page_as_html(file_path: str = None) -> List[types.TextContent]:
    """
    Save the current page's HTML content to a file.

    Args:
        file_path: Optional path to save the HTML file. If not provided, a default path will be used.

    Returns:
        List of TextContent với path to the saved HTML file
    """
    try:
        context = await get_service_context()
        page = await context.playwright_manager.ensure_browser()
        logger.info("Saving current page as HTML")

        if not file_path:
            timestamp = datetime.now().strftime(settings.TIMESTAMP_FORMAT)
            filename = f"{settings.HTML_PREFIX}_{timestamp}.html"
            file_path = settings.get_output_path(filename, "html")

        html_content = await page.content()
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        return [types.TextContent(
            type="text",
            text=f"HTML saved successfully to {file_path}"
        )]
        
    except Exception as e:
        error_msg = f"Failed to save HTML: {str(e)}"
        logger.error(error_msg)
        return [types.TextContent(
            type="text",
            text=error_msg
        )]
