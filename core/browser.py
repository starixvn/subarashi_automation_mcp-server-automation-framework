import asyncio
import logging
from typing import Optional, Dict, Any, List, TYPE_CHECKING
from pathlib import Path

from config.settings import Settings
from core.tab import Tab

if TYPE_CHECKING:
    from playwright.async_api import (
        Browser,
        BrowserContext as PlaywrightBrowserContext,
        Playwright,
        async_playwright,
    )

logger = logging.getLogger(__name__)


class BrowserManager:

    def __init__(self, settings: Settings):
        self.settings = settings
        self.playwright = None
        self.browser: Optional["Browser"] = None
        self.context: Optional["PlaywrightBrowserContext"] = None

    async def start(self):
        try:
            self.playwright = await async_playwright().start()

            if self.settings.browser_type == "chromium":
                self.browser = await self.playwright.chromium.launch(
                    headless=self.settings.headless
                )
            elif self.settings.browser_type == "firefox":
                self.browser = await self.playwright.firefox.launch(
                    headless=self.settings.headless
                )
            elif self.settings.browser_type == "webkit":
                self.browser = await self.playwright.webkit.launch(
                    headless=self.settings.headless
                )
            else:
                self.browser = await self.playwright.chromium.launch(
                    headless=self.settings.headless
                )

            self.context = await self.browser.new_context()
            logger.info(f"Browser started: {self.settings.browser_type}")

        except Exception as e:
            logger.error(f"Failed to start browser: {e}")
            raise

    async def new_tab(self) -> Tab:
        if not self.context:
            await self.start()

        page = await self.context.new_page()
        return Tab(page)

    async def close(self):
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            logger.info("Browser closed")
        except Exception as e:
            logger.error(f"Error closing browser: {e}")


class BrowserContext:

    def __init__(self, context: "PlaywrightBrowserContext"):
        self.context = context

    async def new_page(self):
        return await self.context.new_page()

    async def close(self):
        await self.context.close()
