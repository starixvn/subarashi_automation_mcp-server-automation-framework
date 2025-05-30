import logging
from typing import List
from mcp import types
from mcp_server.core.mcp_setup import mcp, get_service_context

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@mcp.tool(
    name="browser_tab_list",
    description="List all open browser tabs with their details."
)
async def browser_tab_list() -> List[types.TextContent]:
    """
    List all open browser tabs with their details.
    
    Returns:
        List of TextContent with tab information
    """
    try:
        context = await get_service_context()
        page = await context.playwright_manager.ensure_browser()
        browser_context = page.context
        
        pages = browser_context.pages
        current_page = page
        
        if not pages:
            return [types.TextContent(
                type="text",
                text="No browser tabs found"
            )]
        
        tab_info = []
        for i, tab_page in enumerate(pages):
            try:
                title = await tab_page.title()
                url = tab_page.url
                is_current = tab_page == current_page
                status = " (CURRENT)" if is_current else ""
                
                tab_info.append(f"Tab {i}: {title} - {url}{status}")
            except Exception as e:
                tab_info.append(f"Tab {i}: Error getting info - {str(e)}")
        
        result = f"Found {len(pages)} open tabs:\n" + "\n".join(tab_info)
        
        return [types.TextContent(
            type="text",
            text=result
        )]
        
    except Exception as e:
        error_msg = f"Failed to list tabs: {str(e)}"
        logger.error(error_msg)
        return [types.TextContent(
            type="text",
            text=error_msg
        )]


@mcp.tool(
    name="browser_tab_new",
    description="Open a new browser tab and optionally navigate to a URL."
)
async def browser_tab_new(url: str = None) -> List[types.TextContent]:
    """
    Open a new browser tab and optionally navigate to a URL.
    
    Args:
        url: Optional URL to navigate to in the new tab
        
    Returns:
        List of TextContent with new tab information
    """
    try:
        context = await get_service_context()
        page = await context.playwright_manager.ensure_browser()
        browser_context = page.context
        
        logger.info("Creating new browser tab")
        new_page = await browser_context.new_page()
        
        if url:
            logger.info(f"Navigating new tab to: {url}")
            await new_page.goto(url)
            title = await new_page.title()
            result_text = f"Successfully created new tab and navigated to: {url}\nPage title: {title}"
        else:
            result_text = "Successfully created new blank tab"
        
        context.playwright_manager.page = new_page
        
        return [types.TextContent(
            type="text",
            text=result_text
        )]
        
    except Exception as e:
        error_msg = f"Failed to create new tab: {str(e)}"
        logger.error(error_msg)
        return [types.TextContent(
            type="text",
            text=error_msg
        )]


@mcp.tool(
    name="browser_tab_select",
    description="Switch to a specific browser tab by index."
)
async def browser_tab_select(tab_index: int) -> List[types.TextContent]:
    """
    Switch to a specific browser tab by index.
    
    Args:
        tab_index: Index of the tab to switch to (0-based)
        
    Returns:
        List of TextContent with tab switch result
    """
    try:
        if not isinstance(tab_index, int) or tab_index < 0:
            return [types.TextContent(
                type="text",
                text="Error: Tab index must be a non-negative integer"
            )]
        
        context = await get_service_context()
        page = await context.playwright_manager.ensure_browser()
        browser_context = page.context
        
        pages = browser_context.pages
        
        if tab_index >= len(pages):
            return [types.TextContent(
                type="text",
                text=f"Error: Tab index {tab_index} out of range. Available tabs: 0-{len(pages)-1}"
            )]
        
        target_page = pages[tab_index]
        
        await target_page.bring_to_front()
        
        context.playwright_manager.page = target_page
        
        title = await target_page.title()
        url = target_page.url
        
        logger.info(f"Switched to tab {tab_index}: {title}")
        
        return [types.TextContent(
            type="text",
            text=f"Successfully switched to tab {tab_index}: {title} - {url}"
        )]
        
    except Exception as e:
        error_msg = f"Failed to switch to tab: {str(e)}"
        logger.error(error_msg)
        return [types.TextContent(
            type="text",
            text=error_msg
        )]


@mcp.tool(
    name="browser_tab_close",
    description="Close a specific browser tab by index."
)
async def browser_tab_close(tab_index: int = None) -> List[types.TextContent]:
    """
    Close a specific browser tab by index, or current tab if no index specified.
    
    Args:
        tab_index: Index of the tab to close (0-based). If None, closes current tab.
        
    Returns:
        List of TextContent with tab close result
    """
    try:
        context = await get_service_context()
        page = await context.playwright_manager.ensure_browser()
        browser_context = page.context
        
        pages = browser_context.pages
        
        if len(pages) <= 1:
            return [types.TextContent(
                type="text",
                text="Error: Cannot close the last remaining tab"
            )]
        
        if tab_index is None:
            target_page = page
            target_index = pages.index(page)
        else:
            if not isinstance(tab_index, int) or tab_index < 0:
                return [types.TextContent(
                    type="text",
                    text="Error: Tab index must be a non-negative integer"
                )]
            
            if tab_index >= len(pages):
                return [types.TextContent(
                    type="text",
                    text=f"Error: Tab index {tab_index} out of range. Available tabs: 0-{len(pages)-1}"
                )]
            
            target_page = pages[tab_index]
            target_index = tab_index
        
        title = await target_page.title()
        url = target_page.url
        
        await target_page.close()
        
        if target_page == page:
            remaining_pages = browser_context.pages
            if remaining_pages:
                new_current = remaining_pages[0]
                await new_current.bring_to_front()
                context.playwright_manager.page = new_current
        
        logger.info(f"Closed tab {target_index}: {title}")
        
        return [types.TextContent(
            type="text",
            text=f"Successfully closed tab {target_index}: {title} - {url}"
        )]
        
    except Exception as e:
        error_msg = f"Failed to close tab: {str(e)}"
        logger.error(error_msg)
        return [types.TextContent(
            type="text",
            text=error_msg
        )] 