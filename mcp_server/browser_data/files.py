import logging
import os
from typing import List
from mcp import types
from mcp_server.core.mcp_setup import mcp, get_service_context
from mcp_server.config.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@mcp.tool(
    name="browser_file_upload",
    description="Upload a file to a file input element."
)
async def browser_file_upload(
    selector: str,
    file_path: str
) -> List[types.TextContent]:
    """
    Upload a file to a file input element.
    
    Args:
        selector: CSS/XPath selector for the file input element
        file_path: Path to the file to upload
        
    Returns:
        List of TextContent with upload result
    """
    try:
        if not selector or not file_path:
            return [types.TextContent(
                type="text",
                text="Error: Both selector and file_path are required"
            )]
        
        if not settings.validate_selector(selector):
            return [types.TextContent(
                type="text",
                text=f"Error: Selector exceeds maximum length of {settings.MAX_SELECTOR_LENGTH} characters"
            )]
        
        if not os.path.exists(file_path):
            return [types.TextContent(
                type="text",
                text=f"Error: File not found: {file_path}"
            )]
        
        if not os.path.isfile(file_path):
            return [types.TextContent(
                type="text",
                text=f"Error: Path is not a file: {file_path}"
            )]

        context = await get_service_context()
        page = await context.playwright_manager.ensure_browser()
        logger.info(f"Uploading file {file_path} to selector {selector}")
        
        element = await page.query_selector(selector)
        if not element:
            return [types.TextContent(
                type="text",
                text=f"Error: File input element not found with selector: {selector}"
            )]
        
        await element.set_input_files(file_path)
        
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        
        return [types.TextContent(
            type="text",
            text=f"Successfully uploaded file '{file_name}' ({file_size} bytes) to element with selector '{selector}'"
        )]
        
    except Exception as e:
        error_msg = f"Failed to upload file: {str(e)}"
        logger.error(error_msg)
        return [types.TextContent(
            type="text",
            text=error_msg
        )] 