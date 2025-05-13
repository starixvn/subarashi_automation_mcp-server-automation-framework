"""
Content handling functionality for MCP Tools.
Includes content extraction and capture tools.
"""

# Import all content functions
from mcp_tools.server.content.extraction import (
    get_element_html,
    get_element_text,
    get_page_content,
    get_page_html,
    get_page_title,
    save_element_as_html,
    save_page_as_html,
)
from mcp_tools.server.content.capture import (
    browser_save_as_pdf,
    browser_screenshot,
    save_page_screenshot,
)

# Export all functions for easy importing
__all__ = [
    # Capture
    "browser_save_as_pdf",
    "browser_screenshot",
    "save_page_screenshot",
    # Extraction
    "get_element_html",
    "get_element_text",
    "get_page_content",
    "get_page_html",
    "get_page_title",
    "save_element_as_html",
    "save_page_as_html",
]
