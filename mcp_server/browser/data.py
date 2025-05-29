import logging
import json
import psutil
from mcp import types
from mcp_server.core.mcp_setup import mcp, get_service_context
from mcp_server.config.settings import settings
from typing import List
from mcp_server.core.manager import PlaywrightManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@mcp.tool(
    name="clear_browser_data",
    description="Clear cookies, localStorage, and sessionStorage.",
)
async def clear_browser_data() -> List[types.TextContent]:
    """
    Clear cookies, localStorage, and sessionStorage.

    Returns:
        List of TextContent với confirmation message
    """
    try:
        context = await get_service_context()
        page = await context.playwright_manager.ensure_browser()
        logger.info("Clearing browser data")

        # Clear cookies
        await page.context.clear_cookies()
        
        # Clear localStorage and sessionStorage
        await page.evaluate("""() => {
            try {
                localStorage.clear();
                sessionStorage.clear();
                return true;
            } catch (e) {
                console.error('Error clearing storage:', e);
                return false;
            }
        }""")

        return [types.TextContent(
            type="text",
            text="Browser data cleared successfully (cookies, localStorage, sessionStorage)"
        )]
        
    except Exception as e:
        error_msg = f"Failed to clear browser data: {str(e)}"
        logger.error(error_msg)
        return [types.TextContent(
            type="text",
            text=error_msg
        )]


@mcp.tool(name="get_cookies", description="Get all cookies for the current page.")
async def get_cookies() -> List[types.TextContent]:
    """
    Get all cookies for the current page.

    Returns:
        List of TextContent với JSON string of cookies
    """
    try:
        context = await get_service_context()
        page = await context.playwright_manager.ensure_browser()
        logger.info("Getting cookies")

        cookies = await page.context.cookies()
        
        if not cookies:
            return [types.TextContent(
                type="text",
                text="No cookies found for the current page"
            )]
        
        cookies_json = json.dumps(cookies, indent=2, default=str)
        
        return [types.TextContent(
            type="text",
            text=f"Found {len(cookies)} cookies:\n{cookies_json}"
        )]
        
    except Exception as e:
        error_msg = f"Failed to get cookies: {str(e)}"
        logger.error(error_msg)
        return [types.TextContent(
            type="text",
            text=error_msg
        )]


@mcp.tool(
    name="kill_all_chrome_instances",
    description="Kill all Chrome instances generated via Playwright and close browser gracefully.",
)
async def kill_all_chrome_instances() -> List[types.TextContent]:
    """
    Kill all Chrome instances generated via Playwright and close browser gracefully.

    Returns:
        List of TextContent với confirmation message or error message
    """
    try:
        logger.info("Closing browser gracefully first...")
        
        # First, try to close browser gracefully
        try:
            context = await get_service_context()
            if context.playwright_manager:
                await context.playwright_manager.close()
                logger.info("Browser closed gracefully")
        except Exception as graceful_close_error:
            logger.warning(f"Graceful close failed: {str(graceful_close_error)}")

        logger.info("Searching for Chrome processes to terminate...")

        terminated_count = 0
        chrome_processes = []
        
        # Find all Chrome processes
        for process in psutil.process_iter(attrs=["pid", "name", "exe", "cmdline"]):
            try:
                process_info = process.info
                if not process_info["name"]:
                    continue
                    
                name_lower = process_info["name"].lower()
                exe_lower = (process_info["exe"] or "").lower()
                cmdline_str = " ".join(process_info["cmdline"] or []).lower()
                
                # Check if it's a Chrome process, especially from Playwright
                is_chrome = any([
                    "chrome" in name_lower,
                    "chromium" in name_lower,
                    "chrome.exe" in name_lower
                ])
                
                is_playwright_related = any([
                    "playwright" in exe_lower,
                    "playwright" in cmdline_str,
                    "--remote-debugging-port" in cmdline_str,
                    "--user-data-dir" in cmdline_str and "playwright" in cmdline_str
                ])
                
                if is_chrome and (is_playwright_related or not chrome_processes):
                    chrome_processes.append(process)
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue

        # Terminate found processes
        for process in chrome_processes:
            try:
                logger.info(f"Terminating Chrome process: PID {process.pid}")
                process.terminate()
                terminated_count += 1
                
                # Wait a bit for graceful termination
                try:
                    process.wait(timeout=2)
                except psutil.TimeoutExpired:
                    logger.warning(f"Force killing process PID {process.pid}")
                    process.kill()
                    
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                logger.warning(f"Could not terminate process PID {process.pid}: {str(e)}")

        if terminated_count == 0:
            return [types.TextContent(
                type="text",
                text="No Chrome processes found to terminate. Browser may already be closed."
            )]
        else:
            return [types.TextContent(
                type="text",
                text=f"Successfully terminated {terminated_count} Chrome processes."
            )]
        
    except Exception as e:
        error_msg = f"Failed to kill Chrome instances: {str(e)}"
        logger.error(error_msg)
        return [types.TextContent(
            type="text",
            text=error_msg
        )]


@mcp.tool(
    name="browser_close_all",
    description="Close all browser instances and clean up resources completely.",
)
async def browser_close_all() -> List[types.TextContent]:
    """
    Close all browser instances and clean up resources completely.
    This is a comprehensive cleanup function.

    Returns:
        List of TextContent với cleanup confirmation
    """
    try:
        logger.info("Starting comprehensive browser cleanup...")
        
        cleanup_messages = []
        
        # Step 1: Graceful browser close
        try:
            context = await get_service_context()
            if context.playwright_manager:
                await context.playwright_manager.close()
                cleanup_messages.append("✓ Browser closed gracefully")
            else:
                cleanup_messages.append("✓ No active browser manager found")
        except Exception as e:
            cleanup_messages.append(f"⚠ Graceful close failed: {str(e)}")

        # Step 2: Kill remaining Chrome processes
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

        # Step 3: Reset manager state
        try:
            context = await get_service_context()
            if context.playwright_manager:
                # Reset the singleton manager using the proper method
                PlaywrightManager.reset_instance()
                cleanup_messages.append("✓ Browser manager state reset")
        except Exception as e:
            cleanup_messages.append(f"⚠ Manager reset failed: {str(e)}")

        result_message = "Browser cleanup completed:\n" + "\n".join(cleanup_messages)
        
        return [types.TextContent(
            type="text",
            text=result_message
        )]
        
    except Exception as e:
        error_msg = f"Failed to perform complete browser cleanup: {str(e)}"
        logger.error(error_msg)
        return [types.TextContent(
            type="text",
            text=error_msg
        )]
