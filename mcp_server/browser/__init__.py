"""
Browser module cho automation testing framework.
Provides tools for browser navigation, interaction, scrolling, and data management.
"""

# Import browser modules để register tools với MCP server
from mcp_server.browser import navigation
from mcp_server.browser import interaction  
from mcp_server.browser import scrolling
from mcp_server.browser import data

# Export tất cả browser tools
from mcp_server.browser.navigation import (
    browser_navigate,
    browser_close,
    browser_go_back,
    browser_reload,
    get_current_url
)

from mcp_server.browser.interaction import (
    browser_fill,
    browser_click,
    browser_press_key,
    browser_find_by_xpath,
    clear_field
)

from mcp_server.browser.scrolling import (
    browser_scroll_to_top,
    browser_scroll_to_bottom,
    browser_scroll_to_element,
    browser_scroll_one_step
)

from mcp_server.browser.data import (
    clear_browser_data,
    get_cookies,
    kill_all_chrome_instances,
    browser_close_all
)

# Export all tools cho external imports
__all__ = [
    # Navigation tools
    "browser_navigate",
    "browser_close", 
    "browser_go_back",
    "browser_reload",
    "get_current_url",
    
    # Interaction tools
    "browser_fill",
    "browser_click",
    "browser_press_key", 
    "browser_find_by_xpath",
    "clear_field",
    
    # Scrolling tools
    "browser_scroll_to_top",
    "browser_scroll_to_bottom",
    "browser_scroll_to_element",
    "browser_scroll_one_step",
    
    # Data management tools
    "clear_browser_data",
    "get_cookies",
    "kill_all_chrome_instances",
    "browser_close_all"
]
