import os
import nest_asyncio
from mcp.server.fastmcp import FastMCP
from mcp_tools.server.core.manager import PlaywrightManager

nest_asyncio.apply()

mcp = FastMCP(
    name="PlaywrightAutomation", dependencies=["playwright", "nest_asyncio", "psutil"]
)

pw_manager = PlaywrightManager(
    browser_type="chromium", headless=False, viewport_port=(1200, 900)
)

work_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


import mcp_tools.server.browser
import mcp_tools.server.content
import mcp_tools.server.api
import mcp_tools.server.database
import mcp_tools.server.google
