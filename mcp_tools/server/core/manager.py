import logging
import asyncio
from playwright.async_api import async_playwright, Page

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PlaywrightManager:
    """
    A singleton class to manage a single Playwright instance
    to be shared across all MCP tool calls.
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(PlaywrightManager, cls).__new__(cls)
            cls._instance.initialized = False
        return cls._instance

    def __init__(
        self,
        browser_type: str = "chromium",
        headless: bool = True,
        viewport_port: tuple = (1200, 900),
    ):
        if not self.initialized:
            self.browser_type = browser_type
            self.headless = headless
            self.viewport_width, self.viewport_height = viewport_port

            # These will be lazily initialized when needed
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
        if not self.playwright:
            logger.info("Starting Playwright")
            self.playwright = await async_playwright().start()

        if not self.browser:
            logger.info(f"Launching {self.browser_type} browser")
            browser_factory = getattr(self.playwright, self.browser_type)
            self.browser = await browser_factory.launch(headless=self.headless)

            self.context = await self.browser.new_context(
                viewport={"width": self.viewport_width, "height": self.viewport_height}
            )
            logger.info("Browser context created with custom viewport")

            self.page = await self.context.new_page()

        if not self.context:
            logger.info("Creating new browser context")
            self.context = await self.browser.new_context()

        if not self.page:
            logger.info("Creating new page")
            self.page = await self.context.new_page()

        return self.page

    async def close(self) -> None:
        """Close all browser resources explicitly."""
        logger.info("Closing browser resources")

        if self.page:
            await self.page.close()
            self.page = None

        if self.context:
            await self.context.close()
            self.context = None

        if self.browser:
            await self.browser.close()
            self.browser = None

        if self.playwright:
            await self.playwright.stop()
            self.playwright = None
