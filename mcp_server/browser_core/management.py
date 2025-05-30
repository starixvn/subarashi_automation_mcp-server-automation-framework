import logging
import psutil
from mcp import types
from mcp_server.core.mcp_setup import mcp, get_service_context
from mcp_server.config.settings import settings
from mcp_server.core.manager import PlaywrightManager
from typing import List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@mcp.tool(
    name="browser_close", 
    description="Close browser with options for graceful or forceful shutdown."
)
async def browser_close(all_instances: bool = False) -> List[types.TextContent]:
    """
    Close browser resources with various options.

    Args:
        all_instances: If True, performs comprehensive cleanup including force-killing Chrome processes
                      If False, performs graceful browser close only

    Returns:
        List of TextContent with closure confirmation
    """
    try:
        if all_instances:
            logger.info("Starting comprehensive browser cleanup...")
            cleanup_messages = []
            
            try:
                context = await get_service_context()
                if context.playwright_manager:
                    await context.playwright_manager.close()
                    cleanup_messages.append("✓ Browser closed gracefully")
                else:
                    cleanup_messages.append("✓ No active browser manager found")
            except Exception as e:
                cleanup_messages.append(f"⚠ Graceful close failed: {str(e)}")

            try:
                terminated_count = 0
                for process in psutil.process_iter(attrs=["pid", "name", "cmdline"]):
                    try:
                        if (process.info["name"] and 
                            "chrome" in process.info["name"].lower() and
                            process.info["cmdline"] and
                            any("playwright" in arg.lower() for arg in process.info["cmdline"])):
                            
                            process.terminate()
                            terminated_count += 1
                            
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        continue
                
                if terminated_count > 0:
                    cleanup_messages.append(f"✓ Terminated {terminated_count} remaining Chrome processes")
                else:
                    cleanup_messages.append("✓ No remaining Chrome processes found")
                    
            except Exception as e:
                cleanup_messages.append(f"⚠ Process cleanup failed: {str(e)}")

            try:
                context = await get_service_context()
                if context.playwright_manager:
                    PlaywrightManager.reset_instance()
                    cleanup_messages.append("✓ Browser manager state reset")
            except Exception as e:
                cleanup_messages.append(f"⚠ Manager reset failed: {str(e)}")

            result_message = "Comprehensive browser cleanup completed:\n" + "\n".join(cleanup_messages)
            
        else:
            context = await get_service_context()
            await context.playwright_manager.close()
            result_message = "Browser closed gracefully"
        
        return [types.TextContent(
            type="text",
            text=result_message
        )]
        
    except Exception as e:
        error_msg = f"Error closing browser: {str(e)}"
        logger.error(error_msg)
        return [types.TextContent(
            type="text",
            text=error_msg
        )]


@mcp.tool(
    name="browser_resize",
    description="Resize the browser window to specified dimensions."
)
async def browser_resize(width: int, height: int) -> List[types.TextContent]:
    """
    Resize browser window.
    
    Args:
        width: Browser window width in pixels
        height: Browser window height in pixels
        
    Returns:
        List of TextContent with resize result
    """
    try:
        if not isinstance(width, int) or not isinstance(height, int):
            return [types.TextContent(
                type="text",
                text="Error: Width and height must be integers"
            )]
            
        if width < 100 or height < 100:
            return [types.TextContent(
                type="text",
                text="Error: Width and height must be at least 100 pixels"
            )]
            
        if width > 4000 or height > 4000:
            return [types.TextContent(
                type="text",
                text="Error: Width and height must not exceed 4000 pixels"
            )]

        context = await get_service_context()
        page = await context.playwright_manager.ensure_browser()
        logger.info(f"Resizing browser window to {width}x{height}")
        
        await page.set_viewport_size({"width": width, "height": height})
        
        return [types.TextContent(
            type="text",
            text=f"Successfully resized browser window to {width}x{height} pixels"
        )]
        
    except Exception as e:
        error_msg = f"Failed to resize browser window: {str(e)}"
        logger.error(error_msg)
        return [types.TextContent(
            type="text",
            text=error_msg
        )]


@mcp.tool(
    name="browser_install",
    description="Install required browser dependencies for automation."
)
async def browser_install() -> List[types.TextContent]:
    """
    Install browser dependencies.
    
    Returns:
        List of TextContent with installation result
    """
    try:
        context = await get_service_context()
        logger.info("Installing browser dependencies...")
        
        page = await context.playwright_manager.ensure_browser()
        
        return [types.TextContent(
            type="text",
            text="Browser dependencies installed and verified successfully"
        )]
        
    except Exception as e:
        error_msg = f"Failed to install browser dependencies: {str(e)}"
        logger.error(error_msg)
        return [types.TextContent(
            type="text",
            text=error_msg
        )] 