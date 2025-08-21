from typing import TYPE_CHECKING, Optional, List, Dict
import logging

if TYPE_CHECKING:
    from core.tab import Tab
    from core.modal_state import ModalState
    from core.browser_context_factory import BrowserContextManager

logger = logging.getLogger(__name__)


class BrowserRegistry:
    def __init__(self, context_manager: "BrowserContextManager"):
        self.context_manager = context_manager
        self._active_tabs: Dict[str, "Tab"] = {}
        self._modal_states: List["ModalState"] = []

    def register_tab(self, tab_id: str, tab: "Tab") -> None:
        self._active_tabs[tab_id] = tab
        logger.debug(f"Registered tab: {tab_id}")

    def get_tab(self, tab_id: str) -> Optional["Tab"]:
        return self._active_tabs.get(tab_id)

    def remove_tab(self, tab_id: str) -> None:
        if tab_id in self._active_tabs:
            del self._active_tabs[tab_id]
            logger.debug(f"Removed tab: {tab_id}")

    def get_active_tabs(self) -> Dict[str, "Tab"]:
        return self._active_tabs.copy()

    def add_modal_state(self, modal_state: "ModalState") -> None:
        self._modal_states.append(modal_state)
        logger.debug(f"Added modal state: {modal_state.type}")

    def get_modal_states(self) -> List["ModalState"]:
        return self._modal_states.copy()

    def clear_modal_states(self) -> None:
        self._modal_states.clear()
        logger.debug("Cleared all modal states")


def create_browser_registry(
    context_manager: "BrowserContextManager",
) -> BrowserRegistry:
    return BrowserRegistry(context_manager)
