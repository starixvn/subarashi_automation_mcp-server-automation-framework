"""
Content capture and extraction functionality for MCP Server.
Includes screenshot, PDF, and content extraction tools.
"""

from mcp_server.content.capture import (
    browser_save_as_pdf,
    browser_screenshot,
)
from mcp_server.content.extraction import (
    get_element_html,
    get_element_text,
    get_page_content,
    get_page_html,
    get_page_title,
    save_element_as_html,
    save_page_as_html,
)

__all__ = [
    "browser_save_as_pdf",
    "browser_screenshot",
    "get_element_html",
    "get_element_text",
    "get_page_content",
    "get_page_html",
    "get_page_title",
    "save_element_as_html",
    "save_page_as_html",
]
