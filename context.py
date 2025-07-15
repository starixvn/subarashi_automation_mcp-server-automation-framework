import asyncio
import os
import logging
from typing import Optional, List, Dict, Any, TYPE_CHECKING

from config.settings import Settings
from core.modal_state import (
    ModalState,
    ModalStateWithTab,
    DialogModalState,
    FileChooserModalState,
)
from core.download_tracker import DownloadTracker, DownloadEntry
from core.browser_context_factory import (
    create_browser_context_factory,
    get_browser_context_manager,
    BrowserContextResult,
    BrowserContextManager,
)
from core.tab import Tab
from core.registry import EnhancedToolRegistry
from core.tool_schema import ToolCapability
from prompts.registry import PromptRegistry
from resources.registry import ResourceRegistry
from resources.providers import (
    FileSystemResourceProvider,
    BrowserResourceProvider,
    DatabaseResourceProvider,
)
from tools.utils import ManualPromise


if TYPE_CHECKING:
    from playwright.async_api import Dialog, FileChooser, Download, Page

logger = logging.getLogger(__name__)


class ServerContext:
    def __init__(
        self,
        settings: Settings,
        capabilities: Optional[List[str]] = None,
        **factory_kwargs,
    ):
        self.settings: Settings = settings
        self._browser_context_manager = get_browser_context_manager(settings)
        self._browser_context_factory = create_browser_context_factory(
            settings, **factory_kwargs
        )
        self._browser_context_promise: Optional[asyncio.Task[BrowserContextResult]] = (
            None
        )

        self._tabs: List[Tab] = []
        self._current_tab: Optional[Tab] = None
        self._modal_states: List[ModalStateWithTab] = []
        self._download_tracker = DownloadTracker(settings.output_dir)
        self.clientVersion: Optional[Dict[str, str]] = None
        self._pending_action: Optional[Dict[str, Any]] = None
        self.capabilities = capabilities or []

        tool_capabilities = None
        if capabilities:
            tool_capabilities = []
            for cap in capabilities:
                try:
                    tool_capabilities.append(ToolCapability(cap))
                except ValueError:
                    logger.warning(f"Unknown capability: {cap}")

        self.tool_registry: EnhancedToolRegistry = EnhancedToolRegistry(
            self, tool_capabilities
        )

        self.prompt_registry = PromptRegistry()
        self.resource_registry = ResourceRegistry()
        self._setup_resource_providers()

    def _setup_resource_providers(self):
        fs_provider = FileSystemResourceProvider(
            root_paths=[os.getcwd()],
            allowed_extensions=[
                ".txt",
                ".md",
                ".json",
                ".yaml",
                ".yml",
                ".xml",
                ".csv",
                ".log",
                ".py",
                ".js",
                ".ts",
                ".html",
                ".css",
                ".sql",
                ".toml",
                ".ini",
                ".cfg",
                ".conf",
                ".docx",
                ".pdf",
            ],
        )
        self.resource_registry.register_provider("file", fs_provider)

        browser_provider = BrowserResourceProvider(self)
        self.resource_registry.register_provider("browser", browser_provider)

        db_provider = DatabaseResourceProvider()
        self.resource_registry.register_provider("db", db_provider)

        logger.info("Resource providers initialized")

    async def start(self):
        await self._ensure_browser_context()

    def _ensure_browser_context(self) -> asyncio.Task[BrowserContextResult]:
        if self._browser_context_promise is None:
            logger.debug("Creating new browser context promise")
            self._browser_context_promise = asyncio.create_task(
                self._setup_browser_context()
            )
        return self._browser_context_promise

    async def _setup_browser_context(self) -> BrowserContextResult:
        logger.debug("Setting up browser context")

        context_result = await self._browser_context_factory.create_context()
        browser_context = context_result.browser_context

        for page in browser_context.pages:
            self._on_page_created(page)

        browser_context.on("page", self._on_page_created)

        logger.info(
            f"Browser context created with factory: {self._browser_context_factory.name}"
        )
        return context_result

    def _on_page_created(self, page: "Page"):
        tab = Tab(page)

        tab.set_modal_callbacks(
            on_dialog=self._on_dialog_shown,
            on_file_chooser=self._on_file_chooser_shown,
            on_download=self._on_download_started,
        )

        page.on("close", lambda: self._on_page_closed(tab))

        self._tabs.append(tab)

        if self._current_tab is None:
            self._current_tab = tab

        logger.debug(f"New tab created, total tabs: {len(self._tabs)}")

    def _on_page_closed(self, tab: Tab):
        if tab in self._tabs:
            self._tabs.remove(tab)

        self._modal_states = [state for state in self._modal_states if state.tab != tab]

        if self._current_tab == tab:
            self._current_tab = self._tabs[0] if self._tabs else None

        logger.debug(f"Tab closed, remaining tabs: {len(self._tabs)}")

    def tabs(self) -> List[Tab]:
        return self._tabs.copy()

    def current_tab_or_die(self) -> Tab:
        if not self._current_tab:
            raise Exception(
                "No current tab available. Navigate to a page or open a new tab first."
            )
        return self._current_tab

    async def new_tab(self) -> Tab:
        context_result = await self._ensure_browser_context()
        browser_context = context_result.browser_context

        page = await browser_context.new_page()

        new_tab = next((tab for tab in self._tabs if tab.page == page), None)
        if new_tab:
            self._current_tab = new_tab
            return new_tab

        raise Exception("Failed to create new tab")

    async def select_tab(self, index: int):
        if 0 <= index - 1 < len(self._tabs):
            self._current_tab = self._tabs[index - 1]
            await self._current_tab.bring_to_front()
        else:
            raise Exception(f"Tab index {index} out of range")

    async def ensure_tab(self) -> Tab:
        context_result = await self._ensure_browser_context()
        browser_context = context_result.browser_context

        if not self._current_tab:
            await browser_context.new_page()

        return self._current_tab

    async def list_tabs_markdown(self) -> str:
        if not self._tabs:
            return "### No tabs open"

        lines = ["### Open tabs"]
        for i, tab in enumerate(self._tabs):
            title = await tab.title()
            url = tab.url()
            current = " (current)" if tab == self._current_tab else ""
            lines.append(f"- {i + 1}:{current} [{title}] ({url})")

        return "\n".join(lines)

    async def close_tab(self, index: Optional[int] = None) -> str:
        tab = (
            self._current_tab
            if index is None
            else self._tabs[index - 1]
            if 0 <= index - 1 < len(self._tabs)
            else None
        )

        if tab:
            await tab.close()

        return await self.list_tabs_markdown()

    def modal_states(self) -> List[ModalState]:
        return [state.modal_state for state in self._modal_states]

    def set_modal_state(self, modal_state: ModalState, in_tab: Tab):
        state_with_tab = ModalStateWithTab(modal_state, in_tab)
        self._modal_states.append(state_with_tab)
        logger.debug(f"Modal state added: {modal_state.type} in tab {id(in_tab)}")

    def clear_modal_state(self, modal_state: ModalState):
        self._modal_states = [
            state for state in self._modal_states if state.modal_state != modal_state
        ]
        logger.debug(f"Modal state cleared: {modal_state.type}")

    def modal_states_markdown(self) -> List[str]:
        result = ["### Modal state"]

        if not self._modal_states:
            result.append("- There is no modal state present")
        else:
            for state_with_tab in self._modal_states:
                state = state_with_tab.modal_state
                tool = None
                for tool_instance in self.tool_registry.get_all_tools():
                    if tool_instance.clears_modal_state == state.type.value:
                        tool = tool_instance
                        break

                if tool:
                    result.append(
                        f'- [{state.description}]: can be handled by the "{tool.schema.name}" tool'
                    )
                else:
                    result.append(f"- [{state.description}]: no handler found")

        return result

    def _on_dialog_shown(self, tab: Tab, dialog: "Dialog"):
        modal_state = DialogModalState(
            dialog=dialog,
            description=f'"{dialog.type}" dialog with message "{dialog.message}"',
        )
        self.set_modal_state(modal_state, tab)

        if self._pending_action and "dialog_shown" in self._pending_action:
            self._pending_action["dialog_shown"].resolve()

        logger.info(f"Dialog shown in tab: {dialog.message}")

    def _on_file_chooser_shown(self, tab: Tab, file_chooser: "FileChooser"):
        modal_state = FileChooserModalState(
            file_chooser=file_chooser, description="File chooser dialog"
        )
        self.set_modal_state(modal_state, tab)
        logger.info("File chooser shown in tab")

    async def _on_download_started(self, tab: Tab, download: "Download"):
        await self._download_tracker.track_download(download, tab)
        logger.info(f"Download started: {download.suggested_filename}")

    def get_downloads(self) -> List[DownloadEntry]:
        return self._download_tracker.get_downloads()

    def get_downloads_markdown(self) -> List[str]:
        return self._download_tracker.get_downloads_markdown()

    def client_supports_images(self) -> bool:
        if hasattr(self.settings, "image_responses"):
            if self.settings.image_responses == "allow":
                return True
            if self.settings.image_responses == "omit":
                return False

        if (
            self.clientVersion
            and "cursor" in self.clientVersion.get("name", "").lower()
        ):
            return False

        return True

    async def wait_for_timeout(self, time: float):
        if not self._current_tab or self._javascript_blocked():
            await asyncio.sleep(time)
            return

        try:
            await self._current_tab.page.evaluate(
                "() => new Promise(f => setTimeout(f, 1000))"
            )
        except Exception:
            await asyncio.sleep(time)

    def _javascript_blocked(self) -> bool:
        return any(
            state.modal_state.type.value == "dialog" for state in self._modal_states
        )

    async def _race_against_modal_dialogs(self, action):
        self._pending_action = {"dialog_shown": ManualPromise()}

        result = None
        try:

            async def action_coroutine():
                nonlocal result
                result = await action()
                return result

            done, pending = await asyncio.wait(
                [
                    asyncio.create_task(action_coroutine()),
                    asyncio.create_task(
                        self._pending_action["dialog_shown"].as_coroutine()
                    ),
                ],
                return_when=asyncio.FIRST_COMPLETED,
            )

            for task in pending:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass

        finally:
            self._pending_action = None

        return result

    async def create_context_with_factory(
        self, factory_type: str = "default", **kwargs
    ) -> BrowserContextResult:
        return await self._browser_context_manager.create_context(
            factory_type, **kwargs
        )

    def get_context_factory(self, factory_type: str = "default", **kwargs):
        return self._browser_context_manager.get_factory(factory_type, **kwargs)

    async def close(self):
        logger.info("Closing server context")

        for tab in self._tabs.copy():
            try:
                await tab.close()
            except Exception as e:
                logger.error(f"Error closing tab: {e}")

        await self._download_tracker.cleanup()

        try:
            for scheme, provider in self.resource_registry.get_providers().items():
                if hasattr(provider, "_file_watchers"):
                    for watcher in provider._file_watchers.values():
                        watcher.cancel()
                    provider._file_watchers.clear()
                    provider._subscribers.clear()
        except Exception as e:
            logger.error(f"Error cleaning up resource providers: {e}")

        if self._browser_context_promise:
            try:
                context_result = await self._browser_context_promise
                await context_result.close()
            except Exception as e:
                logger.error(f"Error closing browser context: {e}")

        try:
            await self._browser_context_manager.cleanup()
        except Exception as e:
            logger.error(f"Error cleaning up context manager: {e}")

        self._tabs.clear()
        self._current_tab = None
        self._modal_states.clear()
        self._browser_context_promise = None

        logger.info("Server context closed")

    def __str__(self) -> str:
        return f"ServerContext(browser={self.settings.browser_type}, tabs={len(self._tabs)})"
