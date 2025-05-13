import logging
from mcp_tools.server.core.mcp_setup import mcp, pw_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@mcp.tool(name="Browser-Navigate", description="Navigate to a URL in the browser.")
async def browser_navigate(url: str) -> str:
    """
    Navigate to a URL in the browser.

    Args:
        url: The URL to navigate to

    Returns:
        Confirmation message
    """
    if not url or not isinstance(url, str):
        return "Error: URL must be a non-empty string"

    # Ensure browser instance exists
    page = await pw_manager.ensure_browser()
    logger.info(f"Navigating to {url}")

    try:
        await page.goto(url, wait_until="domcontentloaded")
        await page.wait_for_load_state("load", timeout=5000)
    except Exception as e:
        logger.warning(f"Page load timeout or error: {str(e)}")
        return f"Error navigating to {url}: {str(e)}"

    return f"Navigated to {url}"


@mcp.tool(name="Browser-Close", description="Close all browser resources explicitly.")
async def browser_close() -> str:
    """
    Close all browser resources explicitly.

    Returns:
        Closure confirmation
    """
    await pw_manager.close()
    return "Browser closed"


@mcp.tool(
    name="Browser-Go-Back", description="Go back to the previous page in the browser."
)
async def browser_go_back() -> str:
    """
    Go back to the previous page in the browser.

    Returns:
        Navigation result
    """
    page = await pw_manager.ensure_browser()
    logger.info("Navigating back")

    await page.go_back()

    return "Navigated back"


@mcp.tool(name="Browser-Reload", description="Reload the current page.")
async def browser_reload() -> str:
    """
    Reload the current page.

    Returns:
        Reload confirmation
    """
    page = await pw_manager.ensure_browser()
    logger.info("Reloading page")

    await page.reload()

    return "Page reloaded"


@mcp.tool(name="Get-Current-URL", description="Get the URL of the current page.")
async def get_current_url() -> str:
    """
    Get the URL of the current page.

    Returns:
        Current URL
    """
    page = await pw_manager.ensure_browser()
    url = page.url

    return url
