from mcp.server.fastmcp import FastMCP, Context
from context import ServerContext
from services import CoreService


def register_core_tools(app: FastMCP, server_context: ServerContext) -> None:
    @app.tool()
    async def browser_navigate(url: str, context: Context) -> str:
        service = CoreService(server_context)
        nav_result = await service.navigate_to_url(url)
        if not nav_result["success"]:
            return f"Navigation failed: {nav_result['error']}"

        url_result = await service.get_current_url()
        title_result = await service.get_page_title()

        current_url = url_result["data"]["url"] if url_result["success"] else "Unknown"
        page_title = (
            title_result["data"]["title"] if title_result["success"] else "Unknown"
        )

        return f"Successfully navigated to: {current_url}\n Page title: {page_title}\n Status: Navigation completed"

    @app.tool()
    async def browser_close(context: Context) -> str:
        service = CoreService(server_context)
        result = await service.close_browser()
        return result["message"] if result["success"] else f"Error: {result['error']}"

    @app.tool()
    async def browser_resize(width: int, height: int, context: Context) -> str:
        service = CoreService(server_context)
        result = await service.resize_browser(width, height)
        return (
            f"Browser resized to {width}x{height}"
            if result["success"]
            else f"Resize failed: {result['error']}"
        )

    @app.tool()
    async def browser_navigate_back(context: Context) -> str:
        service = CoreService(server_context)
        back_result = await service.go_back()
        if not back_result["success"]:
            return f"Go back failed: {back_result['error']}"

        url_result = await service.get_current_url()
        title_result = await service.get_page_title()

        current_url = url_result["data"]["url"] if url_result["success"] else "Unknown"
        page_title = (
            title_result["data"]["title"] if title_result["success"] else "Unknown"
        )

        return f"Navigated back to: {current_url}\n Page title: {page_title}\n Status: Back navigation completed"

    @app.tool()
    async def browser_navigate_forward(context: Context) -> str:
        service = CoreService(server_context)
        forward_result = await service.go_forward()
        if not forward_result["success"]:
            return f"Go forward failed: {forward_result['error']}"

        url_result = await service.get_current_url()
        title_result = await service.get_page_title()

        current_url = url_result["data"]["url"] if url_result["success"] else "Unknown"
        page_title = (
            title_result["data"]["title"] if title_result["success"] else "Unknown"
        )

        return f"Navigated forward to: {current_url}\n Page title: {page_title}\n Status: Forward navigation completed"

    @app.tool()
    async def browser_reload_page(context: Context) -> str:
        service = CoreService(server_context)
        reload_result = await service.reload_page()
        if not reload_result["success"]:
            return f"Reload failed: {reload_result['error']}"

        url_result = await service.get_current_url()
        title_result = await service.get_page_title()

        current_url = url_result["data"]["url"] if url_result["success"] else "Unknown"
        page_title = (
            title_result["data"]["title"] if title_result["success"] else "Unknown"
        )

        return f"Page reloaded: {current_url}\n Page title: {page_title}\n Status: Reload completed"

