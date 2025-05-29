import os
import nest_asyncio
from mcp.server.fastmcp import FastMCP
from mcp_server.core.manager import PlaywrightManager
from mcp_server.config.settings import settings
from dataclasses import dataclass
from typing import Optional

nest_asyncio.apply()
@dataclass
class ServiceContext:
    """Shared service context cho automation framework."""
    playwright_manager: Optional[PlaywrightManager] = None
    work_directory: Optional[str] = None
    api_client: Optional[object] = None
    sql_client: Optional[object] = None
    sheets_client: Optional[object] = None

service_context = ServiceContext()

service_context.playwright_manager = PlaywrightManager(
    browser_type=settings.BROWSER_TYPE, 
    headless=settings.BROWSER_HEADLESS, 
    viewport_port=settings.get_browser_viewport()
)

service_context.work_directory = settings.OUTPUT_DIRECTORY

async def get_service_context() -> ServiceContext:
    """Get service context dependency."""
    return service_context

async def get_playwright_manager() -> PlaywrightManager:
    """Get playwright manager dependency."""
    return service_context.playwright_manager

async def get_work_directory() -> str:
    """Get work directory dependency."""
    return service_context.work_directory

mcp = FastMCP(
    name="Automation Testing Framework",
    version="1.0.0",
    instructions="Comprehensive automation testing framework with browser automation, API testing, database operations, and Google Sheets integration"
)

pw_manager = service_context.playwright_manager
work_dir = service_context.work_directory

import mcp_server.browser
import mcp_server.content  
import mcp_server.api
import mcp_server.database
import mcp_server.google
import mcp_server.utils
