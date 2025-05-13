import logging
import os
from datetime import datetime
from mcp_tools.server.core.mcp_setup import mcp, pw_manager, work_dir

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@mcp.tool(
    name="Get-Element-HTML",
    description="Get the HTML content of a specific element using XPath.",
)
async def get_element_html(xpath: str) -> str:
    """
    Get the HTML content of a specific element using XPath.

    Args:
        xpath: XPath query to find the element

    Returns:
        HTML content of the element or error message
    """
    if not xpath or not isinstance(xpath, str):
        return "Error: XPath must be a non-empty string"

    page = await pw_manager.ensure_browser()
    logger.info(f"Getting HTML content from element with XPath: {xpath}")

    try:
        element = await page.query_selector(f"xpath={xpath}")
        if not element:
            return f"Error: No element found with XPath: {xpath}"

        html_content = await element.inner_html()
        return html_content
    except Exception as e:
        error_msg = f"Error getting element HTML: {str(e)}"
        logger.error(error_msg)
        return error_msg


@mcp.tool(
    name="Get-Element-Text",
    description="Get the text content of an element using XPath.",
)
async def get_element_text(xpath: str) -> str:
    """
    Get the text content of an element using XPath.

    Args:
        xpath: XPath query to find the element

    Returns:
        Text content of the element or error message
    """
    if not xpath or not isinstance(xpath, str):
        return "Error: XPath must be a non-empty string"

    page = await pw_manager.ensure_browser()
    logger.info(f"Getting text from element with XPath: {xpath}")

    try:
        element = await page.query_selector(f"xpath={xpath}")
        if not element:
            return f"Error: No element found with XPath: {xpath}"

        text = await element.inner_text()
        return text
    except Exception as e:
        error_msg = f"Error getting element text: {str(e)}"
        logger.error(error_msg)
        return error_msg


@mcp.tool(
    name="Get-Page-Content", description="Get the text content of the current page."
)
async def get_page_content() -> str:
    """
    Get the text content of the current page.

    Returns:
        Text content of the page
    """
    page = await pw_manager.ensure_browser()
    text_content = await page.evaluate(
        """() => {
        return document.body.innerText;
    }"""
    )

    return text_content


@mcp.tool(name="Get-Page-HTML", description="Get the HTML content of the current page.")
async def get_page_html() -> str:
    """
    Get the HTML content of the current page.

    Returns:
        HTML content of the page
    """
    page = await pw_manager.ensure_browser()
    html_content = await page.content()

    return html_content


@mcp.tool(name="Get-Page-Title", description="Get the title of the current page.")
async def get_page_title() -> str:
    """
    Get the title of the current page.

    Returns:
        Page title
    """
    page = await pw_manager.ensure_browser()
    title = await page.title()

    return title


@mcp.tool(
    name="Save-Element-As-HTML",
    description="Save a specific element's HTML content to a file using XPath.",
)
async def save_element_as_html(xpath: str, file_path: str = None) -> str:
    """
    Save a specific element's HTML content to a file using XPath.

    Args:
        xpath: XPath query to find the element
        file_path: Optional path to save the HTML file. If not provided, a default path will be used.

    Returns:
        Path to the saved HTML file
    """
    if not xpath or not isinstance(xpath, str):
        return "Error: XPath must be a non-empty string"

    page = await pw_manager.ensure_browser()
    logger.info(f"Saving HTML content of element with XPath: {xpath}")

    if not file_path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(work_dir, f"element_{timestamp}.html")

    try:
        element = await page.query_selector(f"xpath={xpath}")
        if not element:
            return f"Error: No element found with XPath: {xpath}"

        html_content = await element.evaluate("(node) => node.outerHTML")
        if not html_content:
            return f"Error: Could not extract HTML from element with XPath: {xpath}"

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

        # Save to file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(full_html)

        return f"Element HTML saved to {file_path}"
    except Exception as e:
        error_msg = f"Failed to save element HTML: {str(e)}"
        logger.error(error_msg)
        return error_msg


@mcp.tool(
    name="Save-Page-As-HTML",
    description="Save the current page's HTML content to a file.",
)
async def save_page_as_html(file_path: str = None) -> str:
    """
    Save the current page's HTML content to a file.

    Args:
        file_path: Optional path to save the HTML file. If not provided, a default path will be used.

    Returns:
        Path to the saved HTML file
    """
    page = await pw_manager.ensure_browser()
    logger.info("Saving current page as HTML")

    if not file_path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(work_dir, f"page_{timestamp}.html")

    try:
        html_content = await page.content()
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(html_content)
    except Exception as e:
        error_msg = f"Failed to save HTML: {str(e)}"
        logger.error(error_msg)
        return error_msg

    return f"HTML saved to {file_path}"
