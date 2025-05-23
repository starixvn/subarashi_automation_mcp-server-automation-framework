import os
import nest_asyncio
from mcp.server.fastmcp import FastMCP
from mcp_server.core.manager import PlaywrightManager

nest_asyncio.apply()

mcp = FastMCP(
    name="PlaywrightAutomation", dependencies=["playwright", "nest_asyncio", "psutil"]
)

pw_manager = PlaywrightManager(
    browser_type="chromium", headless=True, viewport_port=(1200, 900)
)

work_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import mcp_server.browser
import mcp_server.content
import mcp_server.api
import mcp_server.database
import mcp_server.google
import mcp_server.utils
