import logging
from typing import List
from mcp import types
from mcp_server.core.mcp_setup import mcp, get_service_context
from mcp_server.config.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@mcp.tool(
    name="browser_wait_for",
    description="Wait for a specific condition to be met on the page."
)
async def browser_wait_for(
    condition: str,
    selector: str = None,
    text: str = None,
    timeout: int = 30000
) -> List[types.TextContent]:
    """
    Wait for a specific condition to be met on the page.
    
    Args:
        condition: Condition to wait for ('element_visible', 'element_hidden', 'text_present', 'page_load')
        selector: CSS/XPath selector (required for element conditions)
        text: Text to wait for (required for text_present condition)
        timeout: Maximum time to wait in milliseconds
        
    Returns:
        List of TextContent with wait result
    """
    try:
        valid_conditions = ['element_visible', 'element_hidden', 'text_present', 'page_load']
        if condition not in valid_conditions:
            return [types.TextContent(
                type="text",
                text=f"Error: Condition must be one of {valid_conditions}"
            )]
        
        if condition in ['element_visible', 'element_hidden'] and not selector:
            return [types.TextContent(
                type="text",
                text="Error: Selector is required for element conditions"
            )]
            
        if condition == 'text_present' and not text:
            return [types.TextContent(
                type="text",
                text="Error: Text is required for text_present condition"
            )]
        
        if selector and not settings.validate_selector(selector):
            return [types.TextContent(
                type="text",
                text=f"Error: Selector exceeds maximum length of {settings.MAX_SELECTOR_LENGTH} characters"
            )]
        
        if timeout < 1000 or timeout > 120000:
            return [types.TextContent(
                type="text",
                text="Error: Timeout must be between 1000 and 120000 milliseconds"
            )]

        context = await get_service_context()
        page = await context.playwright_manager.ensure_browser()
        logger.info(f"Waiting for condition: {condition}")
        
        if condition == 'element_visible':
            await page.wait_for_selector(selector, state='visible', timeout=timeout)
            result_text = f"Element with selector '{selector}' became visible"
            
        elif condition == 'element_hidden':
            await page.wait_for_selector(selector, state='hidden', timeout=timeout)
            result_text = f"Element with selector '{selector}' became hidden"
            
        elif condition == 'text_present':
            await page.wait_for_function(
                f"document.body.innerText.includes('{text}')",
                timeout=timeout
            )
            result_text = f"Text '{text}' appeared on the page"
            
        elif condition == 'page_load':
            await page.wait_for_load_state('load', timeout=timeout)
            result_text = "Page finished loading"
        
        return [types.TextContent(
            type="text",
            text=f"Successfully waited for condition: {result_text}"
        )]
        
    except Exception as e:
        error_msg = f"Wait condition failed: {str(e)}"
        logger.error(error_msg)
        return [types.TextContent(
            type="text",
            text=error_msg
        )] 