import logging
import json
import psutil
from mcp_tools.server.core.mcp_setup import mcp, pw_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@mcp.tool(
    name="Clear-Browser-Data",
    description="Clear cookies, localStorage, and sessionStorage.",
)
async def clear_browser_data() -> str:
    """
    Clear cookies, localStorage, and sessionStorage.

    Returns:
        Confirmation message
    """
    page = await pw_manager.ensure_browser()
    logger.info("Clearing browser data")

    await page.context.clear_cookies()
    await page.evaluate("() => { localStorage.clear(); sessionStorage.clear(); }")

    return "Browser data cleared"


@mcp.tool(name="Get-Cookies", description="Get all cookies for the current page.")
async def get_cookies() -> str:
    """
    Get all cookies for the current page.

    Returns:
        JSON string of cookies
    """
    page = await pw_manager.ensure_browser()
    logger.info("Getting cookies")

    cookies = await page.context.cookies()
    return json.dumps(cookies, indent=4)


@mcp.tool(
    name="Kill-All-Chrome-Instances",
    description="Kill all Chrome instances generated via Playwright.",
)
async def kill_all_chrome_instances() -> str:
    """
    Kill all Chrome instances generated via Playwright.

    Returns:
        A confirmation message or an error message.
    """
    logger.info("Attempting to kill all Chrome instances generated via Playwright.")

    try:
        # Iterate through all running processes
        for process in psutil.process_iter(attrs=["pid", "name", "exe"]):
            try:
                # Check if the process name matches Chrome and its executable path contains "playwright"
                if (
                    process.info["name"]
                    and "chrome" in process.info["name"].lower()
                    and process.info["exe"]
                    and "playwright" in process.info["exe"].lower()
                ):
                    logger.info(
                        f'Terminating process: {process.info["name"]} '
                        f'(PID: {process.info["pid"]}, Path: {process.info["exe"]})'
                    )
                    process.terminate()  # Terminate the process
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                logger.warning(f"Could not terminate process: {str(e)}")

        return "All Chrome instances generated via Playwright have been terminated."
    except Exception as e:
        error_msg = f"Failed to kill Chrome instances: {str(e)}"
        logger.error(error_msg)
        return error_msg
