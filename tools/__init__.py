from mcp.server.fastmcp import FastMCP
from typing import TYPE_CHECKING, List, Optional
import logging

if TYPE_CHECKING:
    from context import ServerContext

logger = logging.getLogger(__name__)


def register_all_tools(
    app: FastMCP, context: "ServerContext", capabilities: Optional[List[str]] = None
) -> None:
    if capabilities is None:
        capabilities = [
            "core",
            "vision",
            "tabs",
            "console",
            "keyboard",
            "network",
            "files",
            "wait",
            "api",
            "google_sheets",
            "database",
        ]

    logger.info(f"Registering tools for capabilities: {', '.join(capabilities)}")
    capability_map = {
        "core": _register_core_tools,
        "tabs": _register_tab_tools,
        "vision": _register_vision_tools,
        "console": _register_console_tools,
        "keyboard": _register_keyboard_tools,
        "network": _register_network_tools,
        "files": _register_files_tools,
        "wait": _register_wait_tools,
        "api": _register_api_tools,
        "google_sheets": _register_google_sheets_tools,
        "database": _register_database_tools,
    }

    registered_count = 0

    for capability in capabilities:
        if capability in capability_map:
            try:
                capability_map[capability](app, context)
                registered_count += 1
                logger.debug(f"Registered {capability} tools")
            except Exception as e:
                logger.error(f"Failed to register {capability} tools: {e}")
        else:
            logger.warning(f"Unknown capability: {capability}")

    logger.info(f"Successfully registered {registered_count} tool groups")


def _register_core_tools(app: FastMCP, context: "ServerContext") -> None:
    from .core_tools import register_core_tools
    from .interaction_tools import register_interaction_tools
    from .content_tools import register_content_tools
    from .evaluate_tools import register_evaluate_tools
    from .dialog_tools import register_dialog_tools
    from .snapshot_tools import register_snapshot_tools

    register_core_tools(app, context)
    register_interaction_tools(app, context)
    register_content_tools(app, context)
    register_evaluate_tools(app, context)
    register_dialog_tools(app, context)
    register_snapshot_tools(app, context)


def _register_tab_tools(app: FastMCP, context: "ServerContext") -> None:
    from .tab_tools import register_tab_tools

    register_tab_tools(app, context)


def _register_vision_tools(app: FastMCP, context: "ServerContext") -> None:
    from .vision_tools import register_vision_tools

    register_vision_tools(app, context)


def _register_console_tools(app: FastMCP, context: "ServerContext") -> None:
    from .console_tools import register_console_tools

    register_console_tools(app, context)


def _register_keyboard_tools(app: FastMCP, context: "ServerContext") -> None:
    from .keyboard_tools import register_keyboard_tools

    register_keyboard_tools(app, context)


def _register_network_tools(app: FastMCP, context: "ServerContext") -> None:
    from .network_tools import register_network_tools

    register_network_tools(app, context)


def _register_files_tools(app: FastMCP, context: "ServerContext") -> None:
    from .files_tools import register_files_tools

    register_files_tools(app, context)


def _register_wait_tools(app: FastMCP, context: "ServerContext") -> None:
    from .wait_tools import register_wait_tools

    register_wait_tools(app, context)


def _register_api_tools(app: FastMCP, context: "ServerContext") -> None:
    from .api_tools import register_api_tools

    register_api_tools(app, context)


def _register_google_sheets_tools(app: FastMCP, context: "ServerContext") -> None:
    from .google_sheets_tools import register_google_sheets_tools

    register_google_sheets_tools(app, context)


def _register_database_tools(app: FastMCP, context: "ServerContext") -> None:
    from .database_tools import register_database_tools

    register_database_tools(app, context)


__all__ = ["register_all_tools"]
