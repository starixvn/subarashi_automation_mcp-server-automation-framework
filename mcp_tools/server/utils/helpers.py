import os
import logging
from datetime import datetime
from typing import Optional

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
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
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

    # Very basic validation - real validation would be more complex
    if len(selector.strip()) == 0:
        return False, "Selector cannot be empty or whitespace only"

    return True, None
