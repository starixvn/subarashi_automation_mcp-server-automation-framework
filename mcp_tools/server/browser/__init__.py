"""
Browser interaction functionality for MCP Tools.
Includes navigation, interaction, scrolling, and data management.
"""

# Import all browser functions
from mcp_tools.server.browser.navigation import (
    browser_navigate,
    browser_close,
    browser_go_back,
    browser_reload,
    get_current_url,
)
from mcp_tools.server.browser.interaction import (
    browser_fill,
    browser_click,
    browser_press_key,
    browser_find_by_xpath,
    clear_field,
)
from mcp_tools.server.browser.scrolling import (
    browser_scroll_to_top,
    browser_scroll_to_bottom,
    browser_scroll_to_element,
    browser_scroll_one_step,
)
from mcp_tools.server.browser.data import (
    clear_browser_data,
    get_cookies,
    kill_all_chrome_instances,
)

# Export all functions for easy importing
__all__ = [
    # Navigation
    "browser_navigate",
    "browser_close",
    "browser_go_back",
    "browser_reload",
    "get_current_url",
    # Interaction
    "browser_fill",
    "browser_click",
    "browser_press_key",
    "browser_find_by_xpath",
    "clear_field",
    # Scrolling
    "browser_scroll_to_top",
    "browser_scroll_to_bottom",
    "browser_scroll_to_element",
    "browser_scroll_one_step",
    # Data
    "clear_browser_data",
    "get_cookies",
    "kill_all_chrome_instances",
]
