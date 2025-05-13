"""
Core functionality for MCP Tools.
Contains the PlaywrightManager singleton and MCP setup.
"""

from mcp_tools.server.core.manager import PlaywrightManager
from mcp_tools.server.core.mcp_setup import mcp, pw_manager, work_dir

__all__ = ["PlaywrightManager", "mcp", "pw_manager", "work_dir"]
