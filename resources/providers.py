import logging
import os
import json
from pathlib import Path
from typing import List, Optional, Dict, Any, TYPE_CHECKING

from mcp.server.fastmcp.resources import (
    Resource,
    FileResource,
    FunctionResource,
)
from .models import guess_mime_type
from pydantic import AnyUrl

if TYPE_CHECKING:
    from context import ServerContext

logger = logging.getLogger(__name__)


def create_filesystem_resources(
    root_paths: Optional[List[str]] = None,
    allowed_extensions: Optional[List[str]] = None,
    max_file_size: int = 10 * 1024 * 1024,  # 10MB default
) -> List[Resource]:
    resources = []

    root_paths = root_paths or [os.getcwd()]
    allowed_extensions = set(
        allowed_extensions
        or [
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
        ]
    )

    for root_path_str in root_paths:
        root_path = Path(root_path_str)
        if not root_path.exists():
            logger.warning(f"Root path does not exist: {root_path}")
            continue

        try:
            for file_path in root_path.rglob("*"):
                if file_path.is_file():
                    try:
                        file_size = file_path.stat().st_size
                        if file_size > max_file_size:
                            continue
                    except (OSError, IOError):
                        continue

                    if (
                        allowed_extensions
                        and file_path.suffix.lower() not in allowed_extensions
                    ):
                        continue

                    try:
                        # Create FastMCP FileResource
                        relative_path = file_path.relative_to(root_path).as_posix()
                        uri = AnyUrl(f"file:///{relative_path}")

                        resource = FileResource(
                            uri=uri,
                            path=file_path.absolute(),
                            name=file_path.name,
                            description=f"File: {file_path}",
                            mime_type=guess_mime_type(file_path.name),
                        )
                        resources.append(resource)

                    except (ValueError, OSError) as e:
                        logger.debug(f"Skipping file {file_path}: {e}")

        except Exception as e:
            logger.error(f"Error scanning directory {root_path}: {e}")

    return resources


class FileSystemResourceProvider:
    """DEPRECATED: Use FastMCP FileResource directly instead.

    This class is kept for backward compatibility.
    """

    def __init__(self, *args, **kwargs):
        logger.warning(
            "FileSystemResourceProvider is deprecated. "
            "Use create_filesystem_resources() function instead."
        )

    def __getattr__(self, name):
        raise AttributeError(
            "FileSystemResourceProvider is deprecated. "
            "Use create_filesystem_resources() function and FastMCP FileResource instead."
        )


def create_browser_resources(context: "ServerContext") -> List[Resource]:
    resources = []

    async def get_current_page() -> str:
        try:
            current_tab = context.current_tab_or_die()
            return await current_tab.page.content()
        except Exception as e:
            return f"No active browser page: {str(e)}"

    try:
        current_page_resource = FunctionResource.from_function(
            fn=get_current_page,
            uri="browser://current-page",
            name="Current Page",
            description="Content of the currently active browser page",
            mime_type="text/html",
        )
        resources.append(current_page_resource)
    except Exception as e:
        logger.warning(f"Could not create current page resource: {e}")

    try:
        tabs = context.tabs()
        for i, tab in enumerate(tabs):

            def create_tab_reader(tab_obj, tab_index):
                async def get_tab_content() -> str:
                    try:
                        return await tab_obj.page.content()
                    except Exception as e:
                        return f"Error reading tab {tab_index}: {str(e)}"

                return get_tab_content

            title = "Unknown"
            try:
                title = f"Tab {i + 1}"
            except Exception:
                pass

            try:
                tab_resource = FunctionResource.from_function(
                    fn=create_tab_reader(tab, i),
                    uri=f"browser://tab/{i}",
                    name=f"Tab {i + 1}: {title}",
                    description=f"Content of browser tab {i + 1}",
                    mime_type="text/html",
                )
                resources.append(tab_resource)
            except Exception as e:
                logger.warning(f"Could not create tab {i} resource: {e}")

    except Exception as e:
        logger.debug(f"Error creating tab resources: {e}")

    return resources


class BrowserResourceProvider:
    def __init__(self, *args, **kwargs):
        logger.warning(
            "BrowserResourceProvider is deprecated. "
            "Use create_browser_resources() function instead."
        )

    def __getattr__(self, name):
        raise AttributeError(
            "BrowserResourceProvider is deprecated. "
            "Use create_browser_resources() function and FastMCP FunctionResource instead."
        )


def create_database_resources(connections: Dict[str, Any] = None) -> List[Resource]:
    resources = []
    connections = connections or {}

    for conn_name, connection in connections.items():

        def create_db_info_reader(name, conn):
            async def get_db_info() -> str:
                info = {
                    "connection_name": name,
                    "status": "connected",
                    "available_tables": [],  # Could be populated with actual table info
                }
                return json.dumps(info, indent=2)

            return get_db_info

        try:
            db_resource = FunctionResource.from_function(
                fn=create_db_info_reader(conn_name, connection),
                uri=f"db://{conn_name}/info",
                name=f"Database {conn_name} Info",
                description=f"Connection info for database {conn_name}",
                mime_type="application/json",
            )
            resources.append(db_resource)
        except Exception as e:
            logger.warning(f"Could not create database resource for {conn_name}: {e}")

    return resources


class DatabaseResourceProvider:
    def __init__(self, *args, **kwargs):
        logger.warning(
            "DatabaseResourceProvider is deprecated. "
            "Use create_database_resources() function instead."
        )

    def __getattr__(self, name):
        raise AttributeError(
            "DatabaseResourceProvider is deprecated. "
            "Use create_database_resources() function and FastMCP FunctionResource instead."
        )
