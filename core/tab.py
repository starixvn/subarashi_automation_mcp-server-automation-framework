import asyncio
import logging
from typing import Optional, Dict, Any, List, Callable, TYPE_CHECKING
from pathlib import Path
from playwright.async_api import Page, Dialog, FileChooser, Download

if TYPE_CHECKING:
    from .modal_state import ModalState, DialogModalState, FileChooserModalState
    from .download_tracker import DownloadEntry

from .snapshot import PageSnapshot

logger = logging.getLogger(__name__)


class Tab:
    def __init__(self, page: Page):
        self.page = page
        self.console_messages: List[Dict[str, Any]] = []
        self.network_requests: List[Dict[str, Any]] = []
        self._on_dialog_callback: Optional[Callable] = None
        self._on_file_chooser_callback: Optional[Callable] = None
        self._on_download_callback: Optional[Callable] = None
        self._current_snapshot: Optional[PageSnapshot] = None

        self._setup_listeners()

    def _setup_listeners(self):
        self.page.on("console", self._on_console_message)
        self.page.on("request", self._on_network_request)
        self.page.on("dialog", self._on_dialog)
        self.page.on("filechooser", self._on_file_chooser)
        self.page.on("download", self._on_download)

    def _on_console_message(self, msg):
        self.console_messages.append(
            {
                "type": msg.type,
                "text": msg.text,
                "location": msg.location,
                "timestamp": msg.timestamp if hasattr(msg, "timestamp") else None,
            }
        )

    def _on_network_request(self, request):
        self.network_requests.append(
            {
                "url": request.url,
                "method": request.method,
                "headers": dict(request.headers),
                "timestamp": (
                    request.timing.get("requestTime") if request.timing else None
                ),
            }
        )

    def _on_dialog(self, dialog):
        if self._on_dialog_callback:
            self._on_dialog_callback(self, dialog)

    def _on_file_chooser(self, file_chooser):
        if self._on_file_chooser_callback:
            self._on_file_chooser_callback(self, file_chooser)

    def _on_download(self, download):
        if self._on_download_callback:
            self._on_download_callback(self, download)

    def set_modal_callbacks(
        self,
        on_dialog: Optional[Callable] = None,
        on_file_chooser: Optional[Callable] = None,
        on_download: Optional[Callable] = None,
    ):
        self._on_dialog_callback = on_dialog
        self._on_file_chooser_callback = on_file_chooser
        self._on_download_callback = on_download

    async def navigate(self, url: str) -> str:
        self._clear_collected_artifacts()

        try:
            await self.page.goto(url, wait_until="domcontentloaded")
        except Exception as e:
            might_be_download = "net::ERR_ABORTED" in str(
                e
            ) or "Download is starting" in str(e)
            if not might_be_download:
                raise e

        try:
            await self.wait_for_load_state("load", timeout=5000)
        except Exception:
            pass

        return self.page.url

    async def title(self) -> str:
        try:
            return await self.page.title()
        except Exception as e:
            logger.error(f"Failed to get title: {e}")
            return "Unknown"

    def url(self) -> str:
        return self.page.url

    async def screenshot(self, full_page: bool = False) -> bytes:
        try:
            return await self.page.screenshot(full_page=full_page)
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            raise

    async def click(self, selector: str) -> None:
        try:
            await self.page.click(selector)
        except Exception as e:
            logger.error(f"Click failed on {selector}: {e}")
            raise

    async def type(self, selector: str, text: str) -> None:
        try:
            await self.page.fill(selector, text)
        except Exception as e:
            logger.error(f"Type failed on {selector}: {e}")
            raise

    async def hover(self, selector: str) -> None:
        try:
            await self.page.hover(selector)
        except Exception as e:
            logger.error(f"Hover failed on {selector}: {e}")
            raise

    async def select_option(self, selector: str, value: str) -> None:
        try:
            await self.page.select_option(selector, value)
        except Exception as e:
            logger.error(f"Select option failed on {selector}: {e}")
            raise

    async def get_text(self, selector: str) -> str:
        try:
            return await self.page.text_content(selector) or ""
        except Exception as e:
            logger.error(f"Get text failed on {selector}: {e}")
            raise

    async def wait_for_selector(
        self, selector: str, timeout: Optional[float] = None
    ) -> None:
        try:
            timeout_ms = int(timeout * 1000) if timeout else None
            await self.page.wait_for_selector(selector, timeout=timeout_ms)
        except Exception as e:
            logger.error(f"Wait for selector failed on {selector}: {e}")
            raise

    async def go_back(self) -> None:
        try:
            await self.page.go_back()
        except Exception as e:
            logger.error(f"Go back failed: {e}")
            raise

    async def go_forward(self) -> None:
        try:
            await self.page.go_forward()
        except Exception as e:
            logger.error(f"Go forward failed: {e}")
            raise

    async def reload(self) -> None:
        try:
            await self.page.reload()
        except Exception as e:
            logger.error(f"Reload failed: {e}")
            raise

    async def bring_to_front(self) -> None:
        try:
            await self.page.bring_to_front()
        except Exception as e:
            logger.error(f"Bring to front failed: {e}")
            raise

    async def close(self):
        try:
            await self.page.close()
        except Exception as e:
            logger.error(f"Error closing tab: {e}")

    def get_console_messages(self) -> List[Dict[str, Any]]:
        return self.console_messages.copy()

    def get_network_requests(self) -> List[Dict[str, Any]]:
        return self.network_requests.copy()

    def clear_console_messages(self):
        self.console_messages.clear()

    def clear_network_requests(self):
        self.network_requests.clear()

    def _clear_collected_artifacts(self):
        self.console_messages.clear()
        self.network_requests.clear()

    async def wait_for_load_state(
        self, state: str = "load", timeout: Optional[int] = None
    ) -> None:
        try:
            if timeout:
                await self.page.wait_for_load_state(state, timeout=timeout)
            else:
                await self.page.wait_for_load_state(state)
        except Exception:
            pass

    async def capture_snapshot(self, include_screenshot: bool = True) -> PageSnapshot:
        snapshot = PageSnapshot(self.page)
        await snapshot.capture(include_screenshot=include_screenshot)
        self._current_snapshot = snapshot
        return snapshot

    def has_snapshot(self) -> bool:
        return self._current_snapshot is not None

    def snapshot_or_die(self) -> PageSnapshot:
        if not self._current_snapshot:
            raise Exception("No snapshot available")
        return self._current_snapshot

    def get_current_snapshot(self) -> Optional[PageSnapshot]:
        return self._current_snapshot

    def clear_snapshot(self) -> None:
        self._current_snapshot = None

    def __str__(self) -> str:
        return f"Tab(url={self.url()})"

    def __repr__(self) -> str:
        return self.__str__()
