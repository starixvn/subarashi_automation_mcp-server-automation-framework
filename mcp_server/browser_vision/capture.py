import os
import logging
import base64
from datetime import datetime
from typing import Optional, List
from mcp import types
from mcp_server.core.mcp_setup import mcp, get_service_context
from mcp_server.config.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@mcp.tool(
    name="browser_capture_for_vision",
    description="Take a screenshot and return base64 data for AI vision analysis."
)
async def browser_capture_for_vision(
    full_page: bool = False,
    quality: int = 50
) -> List[types.TextContent]:
    """
    Take a screenshot for AI vision analysis.
    RENAMED from browser_screen_capture for clarity.
    
    Args:
        full_page: Whether to capture the full scrollable page
        quality: JPEG quality (1-100, only for JPEG format)
        
    Returns:
        List of TextContent with screenshot base64 data for vision AI
    """
    try:
        if quality < 1 or quality > 100:
            return [types.TextContent(
                type="text",
                text="Error: Quality must be between 1 and 100"
            )]
        
        context = await get_service_context()
        page = await context.playwright_manager.ensure_browser()
        logger.info(f"Taking vision screenshot (full_page={full_page}, quality={quality})")
        
        screenshot_options = {
            "type": "jpeg",
            "quality": quality,
            "full_page": full_page
        }
        
        screenshot_bytes = await page.screenshot(**screenshot_options)
        screenshot_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')
        
        viewport_size = await page.evaluate("() => ({width: window.innerWidth, height: window.innerHeight})")
        
        result_text = f"""Vision Screenshot Captured for AI Analysis
======================================================

Screenshot Details:
- Format: JPEG (quality: {quality})
- Full page: {full_page}
- Viewport size: {viewport_size['width']}x{viewport_size['height']}
- Data size: {len(screenshot_bytes)} bytes

The screenshot has been captured and is ready for AI vision analysis.
Use coordinate-based tools (browser_screen_click, browser_screen_drag, etc.) 
to interact with elements by their pixel coordinates.

Screenshot data (base64): {screenshot_base64[:100]}...

Full base64 data: {screenshot_base64}
"""

        return [types.TextContent(
            type="text",
            text=result_text
        )]
        
    except Exception as e:
        error_msg = f"Failed to capture screenshot for vision: {str(e)}"
        logger.error(error_msg)
        return [types.TextContent(
            type="text",
            text=error_msg
        )]


@mcp.tool(
    name="browser_save_screenshot",
    description="Take a screenshot and save it to a file."
)
async def browser_save_screenshot(
    selector: str = None, 
    file_path: str = None
) -> List[types.TextContent]:
    """
    Take a screenshot and save it to a file.
    RENAMED from browser_screenshot for clarity.

    Args:
        selector: Optional CSS or XPath selector to capture a specific element
        file_path: Optional path to save the screenshot

    Returns:
        List of TextContent with path to saved screenshot file
    """
    try:
        context = await get_service_context()
        page = await context.playwright_manager.ensure_browser()
        logger.info("Taking screenshot to save to file")

        if not file_path:
            timestamp = datetime.now().strftime(settings.TIMESTAMP_FORMAT)
            filename = f"{settings.SCREENSHOT_PREFIX}_{timestamp}.{settings.SCREENSHOT_FORMAT}"
            file_path = settings.get_output_path(filename, "screenshots")

        screenshot_options = {
            "path": file_path,
            "quality": settings.SCREENSHOT_QUALITY if settings.SCREENSHOT_FORMAT == "jpeg" else None,
            "full_page": settings.SCREENSHOT_FULL_PAGE if not selector else False
        }

        if selector:
            if not settings.validate_selector(selector):
                return [types.TextContent(
                    type="text",
                    text=f"Error: Selector exceeds maximum length of {settings.MAX_SELECTOR_LENGTH} characters"
                )]

            logger.info(f"Taking screenshot of element: {selector}")
            element = await page.query_selector(selector)
            if not element:
                return [types.TextContent(
                    type="text",
                    text=f"Error: Could not find element with selector '{selector}'"
                )]
            
            screenshot_options.pop("full_page", None)
            await element.screenshot(**screenshot_options)
        else:
            await page.screenshot(**screenshot_options)

        return [types.TextContent(
            type="text",
            text=f"Screenshot saved successfully to file: {file_path}"
        )]

    except Exception as e:
        error_msg = f"Failed to take and save screenshot: {str(e)}"
        logger.error(error_msg)
        return [types.TextContent(
            type="text",
            text=error_msg
        )]


@mcp.tool(name="browser_save_as_pdf", description="Save the current page as a PDF file.")
async def browser_save_as_pdf(
    landscape: bool = None, 
    format: str = None
) -> List[types.TextContent]:
    """
    Save the current page as a PDF file.

    Args:
        landscape: Whether to save in landscape orientation (defaults to settings)
        format: Paper format (e.g., 'A4', 'letter') or null for default

    Returns:
        List of TextContent with path to saved PDF file
    """
    try:
        context = await get_service_context()
        
        if context.playwright_manager.browser_type != settings.BROWSER_TYPE:
            await context.playwright_manager.close()
            context.playwright_manager.browser_type = settings.BROWSER_TYPE

        page = await context.playwright_manager.ensure_browser()
        logger.info("Generating PDF")

        landscape = landscape if landscape is not None else settings.PDF_DEFAULT_LANDSCAPE
        format = format or settings.PDF_DEFAULT_FORMAT

        if not settings.validate_pdf_format(format):
            return [types.TextContent(
                type="text",
                text=f"Error: Invalid PDF format '{format}'. Valid formats: {settings.VALID_PDF_FORMATS}"
            )]

        timestamp = datetime.now().strftime(settings.TIMESTAMP_FORMAT)
        filename = f"{settings.PDF_PREFIX}_{timestamp}.pdf"
        file_path = settings.get_output_path(filename, "pdfs")

        pdf_options = {
            "landscape": landscape,
            "format": format,
            "margin": {
                "top": settings.PDF_MARGIN_TOP,
                "right": settings.PDF_MARGIN_RIGHT,
                "bottom": settings.PDF_MARGIN_BOTTOM,
                "left": settings.PDF_MARGIN_LEFT,
            }
        }

        await page.pdf(path=file_path, **pdf_options)
        
        return [types.TextContent(
            type="text",
            text=f"PDF saved successfully to file: {file_path}"
        )]

    except Exception as e:
        error_msg = f"Failed to generate PDF: {str(e)}"
        logger.error(error_msg)
        return [types.TextContent(
            type="text",
            text=error_msg
        )] 