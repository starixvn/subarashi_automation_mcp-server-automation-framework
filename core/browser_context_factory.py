import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Optional, TYPE_CHECKING
from pathlib import Path
import tempfile
from playwright.async_api import async_playwright, Browser, BrowserContext, Playwright

if TYPE_CHECKING:
    from ..config.settings import Settings

logger = logging.getLogger(__name__)


class BrowserContextResult:
    def __init__(self, browser_context: BrowserContext, close_func):
        self.browser_context = browser_context
        self._close_func = close_func

    async def close(self):
        await self._close_func()


class BrowserContextFactory(ABC):
    def __init__(self, settings: "Settings"):
        self.settings = settings
        self.name = "base"

    @abstractmethod
    async def create_context(self) -> BrowserContextResult:
        pass


class BrowserContextManager:
    def __init__(self, settings: "Settings"):
        self.settings = settings
        self._factories: Dict[str, BrowserContextFactory] = {}
        self._current_factory: Optional[BrowserContextFactory] = None

    def get_factory(
        self, factory_type: str = "default", **kwargs
    ) -> BrowserContextFactory:
        factory_key = f"{factory_type}_{hash(frozenset(kwargs.items()))}"

        if factory_key not in self._factories:
            self._factories[factory_key] = self._create_factory(factory_type, **kwargs)

        return self._factories[factory_key]

    def _create_factory(self, factory_type: str, **kwargs) -> BrowserContextFactory:
        if factory_type == "cdp":
            cdp_endpoint = kwargs.get("cdp_endpoint")
            if not cdp_endpoint:
                raise ValueError("CDP endpoint required for CDP factory")
            return CDPContextFactory(self.settings, cdp_endpoint)
        elif factory_type == "isolated":
            return IsolatedContextFactory(self.settings)
        elif factory_type == "persistent":
            return PersistentContextFactory(self.settings)
        else:
            return create_browser_context_factory(self.settings, **kwargs)

    async def create_context(
        self, factory_type: str = "default", **kwargs
    ) -> BrowserContextResult:
        factory = self.get_factory(factory_type, **kwargs)
        self._current_factory = factory
        return await factory.create_context()

    async def cleanup(self):
        for factory in self._factories.values():
            if hasattr(factory, "_browser_promise") and factory._browser_promise:
                try:
                    browser = await factory._browser_promise
                    await browser.close()
                except Exception as e:
                    logger.error(f"Error cleaning up factory: {e}")

        self._factories.clear()
        self._current_factory = None


class BaseBrowserContextFactory(BrowserContextFactory):
    def __init__(self, name: str, settings: "Settings"):
        super().__init__(settings)
        self.name = name
        self._browser_promise: Optional[asyncio.Task] = None

    async def _obtain_browser(self) -> Browser:
        if self._browser_promise and not self._browser_promise.done():
            return await self._browser_promise

        logger.debug(f"Obtaining browser ({self.name})")
        self._browser_promise = asyncio.create_task(self._do_obtain_browser())

        try:
            browser = await asyncio.wait_for(self._browser_promise, timeout=30.0)
            browser.on("disconnected", lambda: setattr(self, "_browser_promise", None))
            return browser
        except asyncio.TimeoutError:
            logger.error(f"Browser startup timeout after 30s ({self.name})")
            if self._browser_promise:
                self._browser_promise.cancel()
                self._browser_promise = None
            raise Exception(
                "Browser startup timeout - server may lack display/resources"
            )
        except Exception as e:
            logger.error(f"Browser startup failed ({self.name}): {e}")
            if self._browser_promise:
                self._browser_promise.cancel()
                self._browser_promise = None
            raise Exception(f"Browser startup failed: {e}")

    @abstractmethod
    async def _do_obtain_browser(self) -> Browser:
        pass

    async def create_context(self) -> BrowserContextResult:
        logger.debug(f"Creating browser context ({self.name})")
        try:
            browser = await self._obtain_browser()
        except Exception as e:
            logger.error(f"Failed to obtain browser: {e}")
            if "timeout" in str(e).lower():
                raise Exception(
                    "Browser startup timeout. On server: ensure headless=true, install browser dependencies, and check system resources."
                )
            else:
                raise Exception(
                    f"Browser initialization failed: {e}. Check if browser binaries are installed and system has sufficient resources."
                )

        try:
            browser_context = await asyncio.wait_for(
                self._do_create_context(browser), timeout=15.0
            )
        except asyncio.TimeoutError:
            logger.error("Browser context creation timeout")
            raise Exception("Browser context timeout - check browser stability")
        except Exception as e:
            logger.error(f"Browser context creation failed: {e}")
            raise Exception(f"Context creation failed: {e}")

        async def close_func():
            await self._close_browser_context(browser_context, browser)

        return BrowserContextResult(browser_context, close_func)

    @abstractmethod
    async def _do_create_context(self, browser: Browser) -> BrowserContext:
        """Actually create the context."""
        pass

    async def _close_browser_context(
        self, browser_context: BrowserContext, browser: Browser
    ):
        logger.debug(f"Closing browser context ({self.name})")

        if len(browser.contexts) == 1:
            self._browser_promise = None

        try:
            await browser_context.close()
        except Exception as e:
            logger.error(f"Error closing browser context: {e}")

        if len(browser.contexts) == 0:
            logger.debug(f"Closing browser ({self.name})")
            try:
                await browser.close()
            except Exception as e:
                logger.error(f"Error closing browser: {e}")


class IsolatedContextFactory(BaseBrowserContextFactory):
    def __init__(self, settings: "Settings"):
        super().__init__("isolated", settings)

    async def _do_obtain_browser(self) -> Browser:
        playwright = await async_playwright().start()

        if self.settings.browser_type == "chromium":
            browser_type = playwright.chromium
        elif self.settings.browser_type == "firefox":
            browser_type = playwright.firefox
        elif self.settings.browser_type == "webkit":
            browser_type = playwright.webkit
        else:
            browser_type = playwright.chromium

        launch_options = {
            "headless": self.settings.headless,
            "handle_sigint": False,
            "handle_sigterm": False,
        }

        try:
            browser = await browser_type.launch(**launch_options)
            browser._playwright = playwright
            return browser
        except Exception as error:
            if "Executable doesn't exist" in str(error):
                raise Exception(
                    "Browser specified in your config is not installed. "
                    "Either install it or change the config."
                )
            raise error

    async def _do_create_context(self, browser: Browser) -> BrowserContext:
        context_options = {"viewport": {"width": 1280, "height": 720}}

        if hasattr(self.settings, "storage_state") and self.settings.storage_state:
            context_options["storage_state"] = self.settings.storage_state

        return await browser.new_context(**context_options)


class PersistentContextFactory(BrowserContextFactory):
    def __init__(self, settings: "Settings"):
        super().__init__(settings)
        self.name = "persistent"
        self._user_data_dirs = set()

    async def create_context(self) -> BrowserContextResult:
        logger.debug("Creating browser context (persistent)")

        user_data_dir = await self._create_user_data_dir()
        self._user_data_dirs.add(user_data_dir)

        playwright = await async_playwright().start()

        if self.settings.browser_type == "chromium":
            browser_type = playwright.chromium
        elif self.settings.browser_type == "firefox":
            browser_type = playwright.firefox
        elif self.settings.browser_type == "webkit":
            browser_type = playwright.webkit
        else:
            browser_type = playwright.chromium

        launch_options = {
            "headless": self.settings.headless,
            "handle_sigint": False,
            "handle_sigterm": False,
        }

        context_options = {"viewport": {"width": 1280, "height": 720}}

        if hasattr(self.settings, "storage_state") and self.settings.storage_state:
            logger.info(
                "PersistentContextFactory: storage_state ignored (using persistent user data directory)"
            )

        options = {**launch_options, **context_options}

        for attempt in range(5):
            try:
                browser_context = await browser_type.launch_persistent_context(
                    user_data_dir, **options
                )

                async def close_func():
                    await self._close_persistent_context(
                        browser_context, user_data_dir, playwright
                    )

                return BrowserContextResult(browser_context, close_func)

            except Exception as error:
                if "Executable doesn't exist" in str(error):
                    raise Exception(
                        "Browser specified in your config is not installed. "
                        "Either install it or change the config."
                    )
                if "ProcessSingleton" in str(error) or "Invalid URL" in str(error):
                    await asyncio.sleep(1)
                    continue
                raise error

        raise Exception(
            f"Browser is already in use for {user_data_dir}, "
            "use isolated mode to run multiple instances"
        )

    async def _close_persistent_context(
        self,
        browser_context: BrowserContext,
        user_data_dir: str,
        playwright: Playwright,
    ):
        logger.debug("Closing browser context (persistent)")

        try:
            await browser_context.close()
        except Exception as e:
            logger.error(f"Error closing persistent context: {e}")

        try:
            await playwright.stop()
        except Exception as e:
            logger.error(f"Error stopping playwright: {e}")

        self._user_data_dirs.discard(user_data_dir)

    async def _create_user_data_dir(self) -> str:
        temp_dir = Path(tempfile.gettempdir())
        mcp_dir = temp_dir / "mcp-automation-server"

        import uuid

        unique_suffix = uuid.uuid4().hex[:8]
        profile_dir = mcp_dir / f"{self.settings.browser_type}-profile-{unique_suffix}"

        profile_dir.mkdir(parents=True, exist_ok=True)
        return str(profile_dir)


class CDPContextFactory(BaseBrowserContextFactory):
    def __init__(self, settings: "Settings", cdp_endpoint: str):
        super().__init__("cdp", settings)
        self.cdp_endpoint = cdp_endpoint

    async def _do_obtain_browser(self) -> Browser:
        playwright = await async_playwright().start()
        try:
            browser = await playwright.chromium.connect_over_cdp(self.cdp_endpoint)
            browser._playwright = playwright
            return browser
        except Exception as error:
            await playwright.stop()
            if "connect" in str(error).lower():
                raise Exception(
                    f"Failed to connect to CDP endpoint {self.cdp_endpoint}. "
                    "Make sure the browser is running with --remote-debugging-port."
                )
            raise error

    async def _do_create_context(self, browser: Browser) -> BrowserContext:
        if getattr(self.settings, "isolated", False):
            context_options = {"viewport": {"width": 1280, "height": 720}}

            if hasattr(self.settings, "storage_state") and self.settings.storage_state:
                logger.info(
                    f"CDPContextFactory (isolated) using storage_state: {self.settings.storage_state}"
                )
                context_options["storage_state"] = self.settings.storage_state

            return await browser.new_context(**context_options)
        else:
            contexts = browser.contexts
            if contexts:
                return contexts[0]
            else:
                context_options = {"viewport": {"width": 1280, "height": 720}}

                if (
                    hasattr(self.settings, "storage_state")
                    and self.settings.storage_state
                ):
                    logger.info(
                        f"CDPContextFactory (new context) using storage_state: {self.settings.storage_state}"
                    )
                    context_options["storage_state"] = self.settings.storage_state

                return await browser.new_context(**context_options)


def create_browser_context_factory(
    settings: "Settings", **kwargs
) -> BrowserContextFactory:
    cdp_endpoint = kwargs.get("cdp_endpoint") or getattr(settings, "cdp_endpoint", None)
    if cdp_endpoint:
        return CDPContextFactory(settings, cdp_endpoint)

    isolated = kwargs.get("isolated", False) or getattr(settings, "isolated", False)
    if isolated:
        return IsolatedContextFactory(settings)

    if hasattr(settings, "storage_state") and settings.storage_state:
        return IsolatedContextFactory(settings)

    persistent = kwargs.get("persistent", True)
    if persistent:
        return PersistentContextFactory(settings)

    return IsolatedContextFactory(settings)


def get_browser_context_manager(settings: "Settings") -> BrowserContextManager:
    return BrowserContextManager(settings)
