import logging
import asyncio
from typing import List
from mcp import types
from mcp_server.core.mcp_setup import mcp, get_service_context
from mcp_server.config.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@mcp.tool(
    name="browser_drag",
    description="Drag and drop from one element to another element."
)
async def browser_drag(
    source_selector: str, 
    target_selector: str
) -> List[types.TextContent]:
    """
    Drag and drop from source element to target element.
    
    Args:
        source_selector: CSS/XPath selector for source element
        target_selector: CSS/XPath selector for target element
        
    Returns:
        List of TextContent with drag result
    """
    try:
        if not source_selector or not target_selector:
            return [types.TextContent(
                type="text", 
                text="Error: Both source and target selectors are required"
            )]
            
        if not settings.validate_selector(source_selector) or not settings.validate_selector(target_selector):
            return [types.TextContent(
                type="text",
                text=f"Error: Selector exceeds maximum length of {settings.MAX_SELECTOR_LENGTH} characters"
            )]

        context = await get_service_context()
        page = await context.playwright_manager.ensure_browser()
        logger.info(f"Dragging from '{source_selector}' to '{target_selector}'")
        
        source_element = await page.query_selector(source_selector)
        target_element = await page.query_selector(target_selector)
        
        if not source_element:
            return [types.TextContent(
                type="text",
                text=f"Error: Source element not found: {source_selector}"
            )]
            
        if not target_element:
            return [types.TextContent(
                type="text", 
                text=f"Error: Target element not found: {target_selector}"
            )]
        
        await source_element.drag_to(target_element)
        
        return [types.TextContent(
            type="text",
            text=f"Successfully dragged element from '{source_selector}' to '{target_selector}'"
        )]
        
    except Exception as e:
        error_msg = f"Failed to perform drag and drop: {str(e)}"
        logger.error(error_msg)
        return [types.TextContent(
            type="text",
            text=error_msg
        )]


@mcp.tool(
    name="browser_handle_dialog",
    description="Handle browser dialogs (alert, confirm, prompt)."
)
async def browser_handle_dialog(
    action: str = "accept",
    prompt_text: str = None
) -> List[types.TextContent]:
    """
    Handle browser dialogs.
    
    Args:
        action: 'accept' or 'dismiss' the dialog
        prompt_text: Text to enter for prompt dialogs
        
    Returns:
        List of TextContent with dialog handling result
    """
    try:
        if action not in ["accept", "dismiss"]:
            return [types.TextContent(
                type="text",
                text="Error: Action must be 'accept' or 'dismiss'"
            )]

        context = await get_service_context()
        page = await context.playwright_manager.ensure_browser()
        logger.info(f"Setting up dialog handler: {action}")
        
        dialog_handled = False
        dialog_info = {}
        
        def handle_dialog(dialog):
            nonlocal dialog_handled, dialog_info
            dialog_info = {
                "type": dialog.type,
                "message": dialog.message,
                "default_value": dialog.default_value if hasattr(dialog, 'default_value') else None
            }
            
            if action == "accept":
                if dialog.type == "prompt" and prompt_text:
                    dialog.accept(prompt_text)
                else:
                    dialog.accept()
            else:
                dialog.dismiss()
            
            dialog_handled = True
        
        page.on("dialog", handle_dialog)
        
        timeout = 10000
        wait_interval = 100
        waited = 0
        
        while not dialog_handled and waited < timeout:
            await asyncio.sleep(wait_interval / 1000)
            waited += wait_interval
        
        page.remove_listener("dialog", handle_dialog)
        
        if not dialog_handled:
            return [types.TextContent(
                type="text",
                text="No dialog appeared within timeout period"
            )]
        
        result_text = f"Successfully {action}ed {dialog_info['type']} dialog"
        if dialog_info.get('message'):
            result_text += f" with message: '{dialog_info['message']}'"
        if prompt_text:
            result_text += f" and entered text: '{prompt_text}'"
        
        return [types.TextContent(
            type="text",
            text=result_text
        )]
        
    except Exception as e:
        error_msg = f"Failed to handle dialog: {str(e)}"
        logger.error(error_msg)
        return [types.TextContent(
            type="text",
            text=error_msg
        )]


@mcp.tool(
    name="browser_console_messages",
    description="Get all console messages (logs, errors, warnings) from the browser."
)
async def browser_console_messages() -> List[types.TextContent]:
    """
    Get all console messages from the browser.
    
    Returns:
        List of TextContent with console messages
    """
    try:
        context = await get_service_context()
        page = await context.playwright_manager.ensure_browser()
        logger.info("Getting console messages")
        
        console_messages = []
        
        def handle_console(msg):
            console_messages.append({
                "type": msg.type,
                "text": msg.text,
                "location": msg.location if hasattr(msg, 'location') else None
            })
        
        page.on("console", handle_console)
        
        await asyncio.sleep(0.5)
        
        if not console_messages:
            return [types.TextContent(
                type="text",
                text="No console messages found"
            )]
        
        formatted_messages = []
        for msg in console_messages:
            level = msg["type"].upper()
            text = msg["text"]
            location = msg["location"]
            
            if location:
                formatted_messages.append(f"[{level}] {text} (at {location})")
            else:
                formatted_messages.append(f"[{level}] {text}")
        
        result = "\n".join(formatted_messages)
        
        return [types.TextContent(
            type="text",
            text=f"Console Messages ({len(console_messages)} total):\n{result}"
        )]
        
    except Exception as e:
        error_msg = f"Failed to get console messages: {str(e)}"
        logger.error(error_msg)
        return [types.TextContent(
            type="text",
            text=error_msg
        )] 