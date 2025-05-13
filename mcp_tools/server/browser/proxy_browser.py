import asyncio
import logging
import json
import uuid
from mcp_tools.server.core.mcp_setup import mcp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Dictionary to store pending commands and their results
pending_commands = {}


class BrowserDelegateManager:
    """Manager for browser delegation to client."""

    @staticmethod
    async def send_browser_command(session, action, args):
        """Send browser command to client."""
        command_id = str(uuid.uuid4())
        command = {
            "type": "browser_command",
            "command_id": command_id,
            "command": {"action": action, "args": args},
        }

        # Create future to wait for response
        future = asyncio.Future()
        pending_commands[command_id] = future

        # Send command to client
        await session.send_custom_message(command)

        try:
            # Wait for result with timeout
            result = await asyncio.wait_for(future, timeout=30.0)
            return result
        except asyncio.TimeoutError:
            del pending_commands[command_id]
            return {"success": False, "error": "Command timed out"}

    @staticmethod
    def receive_browser_result(command_id, result):
        """Process result from client."""
        if command_id in pending_commands:
            future = pending_commands.pop(command_id)
            if not future.done():
                future.set_result(result)
            return True
        return False


# Reimplement all browser functions using the proxy


@mcp.tool(name="Browser-Navigate", description="Navigate to a URL in the browser.")
async def browser_navigate(url: str) -> str:
    """Navigate to a URL in the browser on client machine."""
    if not url or not isinstance(url, str):
        return "Error: URL must be a non-empty string"

    session = mcp._current_session
    result = await BrowserDelegateManager.send_browser_command(
        session, "navigate", {"url": url}
    )

    if result.get("success"):
        return f"Navigated to {url} (title: {result.get('title')})"
    else:
        return f"Error navigating to {url}: {result.get('error')}"


@mcp.tool(name="Browser-Click", description="Click on an element matching the selector")
async def browser_click(selector: str) -> str:
    """Click on an element on client machine browser."""
    if not selector or not isinstance(selector, str):
        return "Error: Selector must be a non-empty string"

    session = mcp._current_session
    result = await BrowserDelegateManager.send_browser_command(
        session, "click", {"selector": selector}
    )

    if result.get("success"):
        return f"Clicked element with selector '{selector}'"
    else:
        return f"Error clicking element: {result.get('error')}"


@mcp.tool(name="Browser-Fill", description="Fill a form field with text.")
async def browser_fill(selector: str, text: str) -> str:
    """Fill a form field on client machine browser."""
    if not selector or not isinstance(selector, str):
        return "Error: Selector must be a non-empty string"
    if not isinstance(text, str):
        return "Error: Text must be a string"

    session = mcp._current_session
    result = await BrowserDelegateManager.send_browser_command(
        session, "fill", {"selector": selector, "text": text}
    )

    if result.get("success"):
        return f"Filled text in element with selector '{selector}'"
    else:
        return f"Error filling element: {result.get('error')}"
