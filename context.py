import asyncio
import os
import logging
import threading
from typing import Optional, List, Dict, Any, TYPE_CHECKING
import weakref

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
)
from core.tab import Tab
from core.registry import create_browser_registry
from prompts.registry import get_default_prompts
from resources.providers import (
    create_filesystem_resources,
    create_browser_resources,
    create_database_resources,
)
from tools.utils import ManualPromise
from mcp.server.lowlevel.server import request_ctx

if TYPE_CHECKING:
    from playwright.async_api import Dialog, FileChooser, Download, Page

logger = logging.getLogger(__name__)


class SessionBrowserContext:
    def __init__(self, session_id: str, server_context: "ServerContext"):
        self.session_id = session_id
        self.server_context = server_context
        self._browser_context_promise: Optional[asyncio.Task[BrowserContextResult]] = (
            None
        )
        self._tabs: List[Tab] = []
        self._current_tab: Optional[Tab] = None
        self._modal_states: List[ModalStateWithTab] = []
        self._download_tracker = DownloadTracker(server_context.settings.output_dir)

    async def ensure_browser_context(self) -> BrowserContextResult:
        if self._browser_context_promise is None:
            logger.info(f"Initializing browser context for session: {self.session_id}")
            self._browser_context_promise = asyncio.create_task(
                self._setup_browser_context()
            )
        return await self._browser_context_promise

    async def _setup_browser_context(self) -> BrowserContextResult:
        context_result = (
            await self.server_context._browser_context_factory.create_context()
        )
        browser_context = context_result.browser_context

        for page in browser_context.pages:
            self._on_page_created(page)

        browser_context.on("page", self._on_page_created)
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

    def _on_page_closed(self, tab: Tab):
        if tab in self._tabs:
            self._tabs.remove(tab)

        self._modal_states = [state for state in self._modal_states if state.tab != tab]

        if self._current_tab == tab:
            self._current_tab = self._tabs[0] if self._tabs else None

    def tabs(self) -> List[Tab]:
        return self._tabs.copy()

    def current_tab_or_die(self) -> Tab:
        if not self._current_tab:
            raise Exception(
                "No current tab available. Navigate to a page or open a new tab first."
            )
        return self._current_tab

    async def new_tab(self) -> Tab:
        context_result = await self.ensure_browser_context()
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
        context_result = await self.ensure_browser_context()
        browser_context = context_result.browser_context

        if not self._current_tab:
            page = await browser_context.new_page()
            new_tab = next((tab for tab in self._tabs if tab.page == page), None)
            if new_tab:
                self._current_tab = new_tab
            else:
                tab = Tab(page)
                tab.set_modal_callbacks(
                    on_dialog=self._on_dialog_shown,
                    on_file_chooser=self._on_file_chooser_shown,
                    on_download=self._on_download_started,
                )
                page.on("close", lambda: self._on_page_closed(tab))
                self._tabs.append(tab)
                self._current_tab = tab

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
        logger.debug(
            f"Modal state added in session {self.session_id}: {modal_state.type} in tab {id(in_tab)}"
        )

    def clear_modal_state(self, modal_state: ModalState):
        self._modal_states = [
            state for state in self._modal_states if state.modal_state != modal_state
        ]
        logger.debug(
            f"Modal state cleared in session {self.session_id}: {modal_state.type}"
        )

    def modal_states_markdown(self) -> List[str]:
        result = ["### Modal state"]

        if not self._modal_states:
            result.append("- There is no modal state present")
        else:
            for state_with_tab in self._modal_states:
                state = state_with_tab.modal_state
                result.append(f"- [{state.description}]: modal state present")

        return result

    def _on_dialog_shown(self, tab: Tab, dialog: "Dialog"):
        modal_state = DialogModalState(
            dialog=dialog,
            description=f'"{dialog.type}" dialog with message "{dialog.message}"',
        )
        self.set_modal_state(modal_state, tab)
        logger.info(f"Dialog shown in session {self.session_id}: {dialog.message}")

    def _on_file_chooser_shown(self, tab: Tab, file_chooser: "FileChooser"):
        modal_state = FileChooserModalState(
            file_chooser=file_chooser, description="File chooser dialog"
        )
        self.set_modal_state(modal_state, tab)
        logger.info(f"File chooser shown in session {self.session_id}")

    async def _on_download_started(self, tab: Tab, download: "Download"):
        await self._download_tracker.track_download(download, tab)
        logger.info(
            f"Download started in session {self.session_id}: {download.suggested_filename}"
        )

    def get_downloads(self) -> List[DownloadEntry]:
        return self._download_tracker.get_downloads()

    def get_downloads_markdown(self) -> List[str]:
        return self._download_tracker.get_downloads_markdown()

    async def cleanup(self):
        for tab in self._tabs.copy():
            try:
                await tab.close()
            except Exception as e:
                logger.error(f"Error closing tab in session {self.session_id}: {e}")

        await self._download_tracker.cleanup()

        if self._browser_context_promise:
            try:
                context_result = await self._browser_context_promise
                await context_result.close()
            except Exception as e:
                logger.error(
                    f"Error closing browser context in session {self.session_id}: {e}"
                )

        self._tabs.clear()
        self._current_tab = None
        self._modal_states.clear()
        self._browser_context_promise = None


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

        self._session_contexts: Dict[str, SessionBrowserContext] = {}
        self._session_refs: weakref.WeakValueDictionary = weakref.WeakValueDictionary()

        self._current_session_id = threading.local()

        self.clientVersion: Optional[Dict[str, str]] = None
        self._pending_action: Optional[Dict[str, Any]] = None
        self.capabilities = capabilities or []
        self.browser_registry = create_browser_registry(self._browser_context_manager)
        self.prompts = get_default_prompts()
        self.resources = self._setup_resources()

        logger.info("ServerContext initialized with session-based browser contexts")

    def set_current_session_id(self, session_id: str):
        self._current_session_id.value = session_id

    def get_current_session_id(self) -> Optional[str]:
        return getattr(self._current_session_id, "value", None)

    def _setup_resources(self):
        resources = []

        try:
            fs_resources = create_filesystem_resources(
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
            resources.extend(fs_resources)
        except Exception as e:
            logger.warning(f"Could not create filesystem resources: {e}")
        try:
            browser_resources = create_browser_resources(self)
            resources.extend(browser_resources)
        except Exception as e:
            logger.warning(f"Could not create browser resources: {e}")

        try:
            db_resources = create_database_resources({})
            resources.extend(db_resources)
        except Exception as e:
            logger.warning(f"Could not create database resources: {e}")

        return resources

    async def start(self):
        logger.info(
            "Server context started - browsers will be initialized per-session when needed"
        )

    def get_session_id(self) -> str:
        try:
            context = request_ctx.get()
            if context and context.request:
                request_data = context.request

                if hasattr(request_data, "query_params"):
                    session_id = request_data.query_params.get("session_id")
                    if session_id:
                        return session_id

                if hasattr(request_data, "headers"):
                    session_id = request_data.headers.get("mcp-session-id")
                    if session_id:
                        return session_id

            if context and context.session:
                session_id = str(id(context.session))
                return f"session_{session_id}"

        except (LookupError, AttributeError):
            pass

        return "default_session"

    def get_session_browser_context(
        self, session_id: Optional[str] = None
    ) -> SessionBrowserContext:
        if session_id is None:
            session_id = self.get_session_id()

        if session_id not in self._session_contexts:
            logger.info(f"Creating new browser session context: {session_id}")
            self._session_contexts[session_id] = SessionBrowserContext(session_id, self)

        return self._session_contexts[session_id]

    def tabs(self) -> List[Tab]:
        session_context = self.get_session_browser_context()
        return session_context.tabs()

    def current_tab_or_die(self) -> Tab:
        session_context = self.get_session_browser_context()
        return session_context.current_tab_or_die()

    async def new_tab(self) -> Tab:
        session_context = self.get_session_browser_context()
        return await session_context.new_tab()

    async def select_tab(self, index: int):
        session_context = self.get_session_browser_context()
        await session_context.select_tab(index)

    async def ensure_tab(self) -> Tab:
        session_context = self.get_session_browser_context()
        return await session_context.ensure_tab()

    async def list_tabs_markdown(self) -> str:
        session_context = self.get_session_browser_context()
        return await session_context.list_tabs_markdown()

    async def close_tab(self, index: Optional[int] = None) -> str:
        session_context = self.get_session_browser_context()
        return await session_context.close_tab(index)

    def modal_states(self) -> List[ModalState]:
        session_context = self.get_session_browser_context()
        return session_context.modal_states()

    def set_modal_state(self, modal_state: ModalState, in_tab: Tab):
        session_context = self.get_session_browser_context()
        session_context.set_modal_state(modal_state, in_tab)

    def clear_modal_state(self, modal_state: ModalState):
        session_context = self.get_session_browser_context()
        session_context.clear_modal_state(modal_state)

    def modal_states_markdown(self) -> List[str]:
        session_context = self.get_session_browser_context()
        return session_context.modal_states_markdown()

    def get_downloads(self) -> List[DownloadEntry]:
        session_context = self.get_session_browser_context()
        return session_context.get_downloads()

    def get_downloads_markdown(self) -> List[str]:
        session_context = self.get_session_browser_context()
        return session_context.get_downloads_markdown()

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
        for session_id, session_context in list(self._session_contexts.items()):
            try:
                await session_context.cleanup()
            except Exception as e:
                logger.error(f"Error cleaning up session {session_id}: {e}")

        self._session_contexts.clear()

        try:
            logger.debug("Cleaning up FastMCP resources")
        except Exception as e:
            logger.error(f"Error cleaning up resources: {e}")

        try:
            await self._browser_context_manager.cleanup()
        except Exception as e:
            logger.error(f"Error cleaning up context manager: {e}")

        logger.info("Server context closed")
