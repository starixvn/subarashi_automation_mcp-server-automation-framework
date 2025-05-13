"""
MCP Tools for Playwright browser automation.
A modular framework for browser automation using Playwright and MCP.
"""

__version__ = "0.1.0"

# Import core components
from mcp_tools.server.core import mcp, pw_manager, PlaywrightManager

# Ensure all modules are imported to register tools
import mcp_tools.server.browser
import mcp_tools.server.content
import mcp_tools.server.api
import mcp_tools.server.database
import mcp_tools.server.google

# Import individual components for direct access
# Browser module
from mcp_tools.server.browser import (
    browser_navigate,
    browser_close,
    browser_go_back,
    browser_reload,
    get_current_url,
    browser_fill,
    browser_click,
    browser_press_key,
    browser_find_by_xpath,
    clear_field,
    browser_scroll_to_top,
    browser_scroll_to_bottom,
    browser_scroll_to_element,
    browser_scroll_one_step,
    clear_browser_data,
    get_cookies,
    kill_all_chrome_instances,
)

# Content module
from mcp_tools.server.content import (
    browser_save_as_pdf,
    browser_screenshot,
    save_page_screenshot,
    get_element_html,
    get_element_text,
    get_page_content,
    get_page_html,
    get_page_title,
    save_element_as_html,
    save_page_as_html,
)

# API module
from mcp_tools.server.api import (
    api_init,
    api_get,
    api_post,
    api_put,
    api_delete,
    api_basic_auth,
    api_bearer_token,
    api_oauth2_client_credentials,
    api_clear_auth,
)

# Database module
from mcp_tools.server.database import (
    SQLServerClient,
    db_connect,
    db_connect_with_string,
    db_query,
    db_execute,
    db_execute_many,
    db_execute_script,
    db_get_tables,
    db_get_columns,
    db_close,
)

# Google module
from mcp_tools.server.google import (
    GoogleSheetsClient,
    google_sheets_init,
    google_sheets_read,
    google_sheets_write,
    google_sheets_append,
    google_sheets_clear,
    google_sheets_create_sheet,
    google_sheets_get_sheets,
)

# Export key components for easier imports
__all__ = [
    # Core components
    "mcp",
    "pw_manager",
    "PlaywrightManager",
    # Browser module
    "browser_navigate",
    "browser_close",
    "browser_go_back",
    "browser_reload",
    "get_current_url",
    "browser_fill",
    "browser_click",
    "browser_press_key",
    "browser_find_by_xpath",
    "clear_field",
    "browser_scroll_to_top",
    "browser_scroll_to_bottom",
    "browser_scroll_to_element",
    "browser_scroll_one_step",
    "clear_browser_data",
    "get_cookies",
    "kill_all_chrome_instances",
    # Content module
    "browser_save_as_pdf",
    "browser_screenshot",
    "save_page_screenshot",
    "get_element_html",
    "get_element_text",
    "get_page_content",
    "get_page_html",
    "get_page_title",
    "save_element_as_html",
    "save_page_as_html",
    # API module
    "api_init",
    "api_get",
    "api_post",
    "api_put",
    "api_delete",
    "api_basic_auth",
    "api_bearer_token",
    "api_oauth2_client_credentials",
    "api_clear_auth",
    # Database module
    "SQLServerClient",
    "db_connect",
    "db_connect_with_string",
    "db_query",
    "db_execute",
    "db_execute_many",
    "db_execute_script",
    "db_get_tables",
    "db_get_columns",
    "db_close",
    # Google module
    "GoogleSheetsClient",
    "google_sheets_init",
    "google_sheets_read",
    "google_sheets_write",
    "google_sheets_append",
    "google_sheets_clear",
    "google_sheets_create_sheet",
    "google_sheets_get_sheets",
]
