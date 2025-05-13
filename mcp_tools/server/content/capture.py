import logging
import os
import tempfile
from datetime import datetime
from mcp_tools.server.core.mcp_setup import mcp, pw_manager, work_dir

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@mcp.tool(name="Browser-Save-As-PDF", description="Save the current page as a PDF.")
async def browser_save_as_pdf(landscape: bool = False, format: str = None) -> str:
    """
    Save the current page as a PDF.

    Args:
        landscape: Whether to save in landscape orientation
        format: Paper format (e.g., 'A4', 'letter') or null for default

    Returns:
        Path to saved PDF file
    """
    if pw_manager.browser_type != "chromium" or not pw_manager.headless:
        await pw_manager.close()

        pw_manager.browser_type = "chromium"
        pw_manager.headless = False

    page = await pw_manager.ensure_browser()
    logger.info("Generating PDF")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = os.path.join(tempfile.gettempdir(), f"page_{timestamp}.pdf")

    pdf_options = {}
    if landscape:
        pdf_options["landscape"] = True
    if format:
        pdf_options["format"] = format

    try:
        await page.pdf(path=file_name, **pdf_options)
    except Exception as e:
        error_msg = f"Failed to generate PDF: {str(e)}"
        logger.error(error_msg)
        return error_msg

    return f"PDF saved to {file_name}"


@mcp.tool(
    name="Browser-Screenshot",
    description="Take a screenshot of the current page or a specific element.",
)
async def browser_screenshot(selector: str = None, file_path: str = None) -> str:
    """
    Take a screenshot of the current page or a specific element.

    Args:
        selector: Optional CSS or XPath selector to capture a specific element
        file_path: Optional path to save the screenshot

    Returns:
        Path to saved screenshot
    """
    page = await pw_manager.ensure_browser()
    logger.info("Taking screenshot")

    if not file_path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(tempfile.gettempdir(), f"screenshot_{timestamp}.png")

    try:
        if selector:
            logger.info(f"Taking screenshot of element: {selector}")
            element = await page.query_selector(selector)
            if not element:
                return f"Error: Could not find element with selector '{selector}'"
            await element.screenshot(path=file_path)
        else:
            await page.screenshot(path=file_path)
    except Exception as e:
        error_msg = f"Failed to take screenshot: {str(e)}"
        logger.error(error_msg)
        return error_msg

    return f"Screenshot saved to {file_path}"


@mcp.tool(
    name="Save-Page-Screenshot", description="Save a screenshot of the current page."
)
async def save_page_screenshot(file_path: str = None) -> str:
    """
    Save a screenshot of the current page.

    Args:
        file_path: Optional path to save the screenshot. If not provided, a default path will be used.

    Returns:
        Path to the saved screenshot
    """
    page = await pw_manager.ensure_browser()
    logger.info("Taking screenshot of the current page")

    if not file_path:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(work_dir, f"screenshot_{timestamp}.png")
    else:
        file_path = os.path.join(file_path)

    try:
        await page.screenshot(path=file_path)
    except Exception as e:
        error_msg = f"Failed to take screenshot: {str(e)}"
        logger.error(error_msg)
        return error_msg

    return f"Screenshot saved to {file_path}"
