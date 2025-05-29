import os
import re
import logging
from datetime import datetime
from typing import Optional
from mcp_server.config.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def generate_timestamp_filename(
    prefix: str, extension: str, directory: Optional[str] = None
) -> str:
    """
    Generate a filename with a timestamp.

    Args:
        prefix: Prefix for the filename
        extension: File extension (without the dot)
        directory: Optional directory to save the file in

    Returns:
        Full path to the file
    """
    timestamp = datetime.now().strftime(settings.TIMESTAMP_FORMAT)
    filename = f"{prefix}_{timestamp}.{extension}"

    if directory:
        if not os.path.exists(directory):
            os.makedirs(directory)
        return os.path.join(directory, filename)

    return filename


def format_xpath(xpath: str) -> str:
    """
    Format an XPath expression to ensure it's properly formatted for Playwright.

    Args:
        xpath: The XPath expression to format

    Returns:
        Properly formatted XPath expression
    """
    if not xpath:
        return ""

    if len(xpath) > settings.MAX_XPATH_LENGTH:
        logger.warning(f"XPath exceeds maximum length of {settings.MAX_XPATH_LENGTH} characters")
        return ""

    if xpath.startswith("xpath="):
        return xpath

    if xpath.startswith("//"):
        return f"xpath={xpath}"

    return f"xpath=//{xpath}"


def validate_selector(selector: str) -> tuple[bool, Optional[str]]:
    """
    Validate a CSS or XPath selector.

    Args:
        selector: The selector to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not selector or not isinstance(selector, str):
        return False, "Selector must be a non-empty string"

    if len(selector.strip()) == 0:
        return False, "Selector cannot be empty or whitespace only"

    if not settings.validate_selector(selector):
        return False, f"Selector exceeds maximum length of {settings.MAX_SELECTOR_LENGTH} characters"

    return True, None


def validate_url(url: str) -> tuple[bool, Optional[str]]:
    """
    Validate a URL using settings constraints.

    Args:
        url: The URL to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not url or not isinstance(url, str):
        return False, "URL must be a non-empty string"

    if not settings.validate_url(url):
        return False, f"URL exceeds maximum length of {settings.MAX_URL_LENGTH} characters"

    for blocked_domain in settings.BLOCKED_DOMAINS:
        if blocked_domain in url.lower():
            return False, f"URL contains blocked domain: {blocked_domain}"

    if settings.ALLOWED_DOMAINS:
        allowed = False
        for allowed_domain in settings.ALLOWED_DOMAINS:
            if allowed_domain in url.lower():
                allowed = True
                break
        if not allowed:
            return False, f"URL not in allowed domains: {settings.ALLOWED_DOMAINS}"

    return True, None
