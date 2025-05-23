"""
Content handling functionality for MCP Server.
Includes content extraction and capture tools.
"""

from mcp_server.content.extraction import (
    get_element_html,
    get_element_text,
    get_page_content,
    get_page_html,
    get_page_title,
    save_element_as_html,
    save_page_as_html,
)
from mcp_server.content.capture import (
    browser_save_as_pdf,
    browser_screenshot,
    save_page_screenshot,
)

__all__ = [
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
]
