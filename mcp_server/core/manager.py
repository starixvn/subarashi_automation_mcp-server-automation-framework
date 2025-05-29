import logging
import asyncio
from playwright.async_api import async_playwright, Page
from mcp_server.config.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PlaywrightManager:
    """
    A singleton class to manage a single Playwright instance
    to be shared across all MCP tool calls.
    """

    _instance = None
    _lock = asyncio.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(PlaywrightManager, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(
        self,
        browser_type: str = None,
        headless: bool = None,
        viewport_port: tuple = None,
    ):
        if not self.initialized:
            self.browser_type = browser_type or settings.BROWSER_TYPE
            self.headless = headless if headless is not None else settings.BROWSER_HEADLESS
            self.viewport_width, self.viewport_height = viewport_port or settings.get_browser_viewport()
            self.playwright = None
            self.browser = None
            self.context = None
            self.page = None
            self.initialized = True

    async def ensure_browser(self) -> Page:
        """
        Ensure browser is initialized and return the page.

        Returns:
            Active Playwright page
        """
        async with self._lock:
            if not self.playwright:
                logger.info("Starting Playwright")
                self.playwright = await async_playwright().start()

            if not self.browser:
                logger.info(f"Launching {self.browser_type} browser")
                
                if not settings.validate_browser_type(self.browser_type):
                    logger.warning(f"Invalid browser type {self.browser_type}, falling back to chromium")
                    self.browser_type = settings.BROWSER_TYPE
                    
                browser_factory = getattr(self.playwright, self.browser_type)
                self.browser = await browser_factory.launch(headless=self.headless)

                self.context = await self.browser.new_context(
                    viewport={"width": self.viewport_width, "height": self.viewport_height}
                )
                logger.info(f"Browser context created with viewport {self.viewport_width}x{self.viewport_height}")

                self.page = await self.context.new_page()

            if not self.context:
                logger.info("Creating new browser context")
                self.context = await self.browser.new_context(
                    viewport={"width": self.viewport_width, "height": self.viewport_height}
                )

            if not self.page:
                logger.info("Creating new page")
                self.page = await self.context.new_page()

            return self.page

    async def close(self) -> None:
        """Close all browser resources explicitly."""
        async with self._lock:
            logger.info("Closing browser resources")

            try:
                if self.page:
                    await self.page.close()
                    self.page = None
                    logger.debug("Page closed")
            except Exception as e:
                logger.warning(f"Error closing page: {e}")

            try:
                if self.context:
                    await self.context.close()
                    self.context = None
                    logger.debug("Context closed")
            except Exception as e:
                logger.warning(f"Error closing context: {e}")

            try:
                if self.browser:
                    await self.browser.close()
                    self.browser = None
                    logger.debug("Browser closed")
            except Exception as e:
                logger.warning(f"Error closing browser: {e}")

            try:
                if self.playwright:
                    await self.playwright.stop()
                    self.playwright = None
                    logger.debug("Playwright stopped")
            except Exception as e:
                logger.warning(f"Error stopping playwright: {e}")
                
            logger.info("Browser resources cleanup completed")
    
    @classmethod
    def reset_instance(cls):
        """Reset the singleton instance. Use with caution."""
        cls._instance = None
        logger.info("PlaywrightManager singleton instance reset")

    def is_active(self) -> bool:
        """Check if the browser is currently active."""
        return all([self.playwright, self.browser, self.context, self.page])
