from typing import Optional
from mcp.server.fastmcp import FastMCP, Context
from context import ServerContext
from services import WaitService
from services import CoreService


def register_wait_tools(app: FastMCP, server_context: ServerContext) -> None:
    @app.tool(description="Wait for a condition")
    async def browser_wait_for(
        wait_type: str,
        context: Context,
        timeout: Optional[int] = None,
        selector: Optional[str] = None,
        text: Optional[str] = None,
    ) -> str:
        service = WaitService(server_context)

        if wait_type == "timeout":
            if timeout is None:
                return "Error: timeout parameter is required for 'timeout' wait type"

            result = await service.wait_for_timeout(timeout / 1000.0)
            return (
                f"Waited for {timeout}ms"
                if result.success
                else f"Wait timeout failed: {result.error}"
            )

        elif wait_type == "element":
            if selector is None:
                return "Error: selector parameter is required for 'element' wait type"

            timeout_seconds = (timeout or 30000) / 1000.0
            result = await service.wait_for_selector(selector, timeout_seconds)

            if not result.success:
                return f"Element {selector} did not appear within {timeout or 30000}ms: {result.error}"

            core_service = CoreService(server_context)
            url_result = await core_service.get_current_url()
            title_result = await core_service.get_page_title()

            current_url = (
                url_result["data"]["url"] if url_result["success"] else "Unknown"
            )
            page_title = (
                title_result["data"]["title"] if title_result["success"] else "Unknown"
            )

            return f"Element {selector} appeared\n URL: {current_url}\n Title: {page_title}\n Status: Element wait completed"

        elif wait_type == "text":
            if text is None:
                return "Error: text parameter is required for 'text' wait type"

            result = await service.wait_for_text(text)
            if not result.success:
                return f"Failed to find text '{text}': {result.error}"

            core_service = CoreService(server_context)
            url_result = await core_service.get_current_url()
            title_result = await core_service.get_page_title()

            current_url = (
                url_result["data"]["url"] if url_result["success"] else "Unknown"
            )
            page_title = (
                title_result["data"]["title"] if title_result["success"] else "Unknown"
            )

            return f"Text '{text}' appeared on page\n URL: {current_url}\n Title: {page_title}\n Status: Text wait completed"

        elif wait_type == "text_gone":
            if text is None:
                return "Error: text parameter is required for 'text_gone' wait type"

            result = await service.wait_for_text_gone(text)
            return (
                f"Text '{text}' disappeared from page"
                if result.success
                else f"Text '{text}' still present: {result.error}"
            )

        else:
            return f"Error: Invalid wait_type '{wait_type}'. Valid options: 'timeout', 'element', 'text', 'text_gone'"
