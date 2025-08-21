from mcp.server.fastmcp import FastMCP, Context
from context import ServerContext
from services import TabsService
from services import CoreService


def register_tab_tools(app: FastMCP, server_context: ServerContext) -> None:
    @app.tool()
    async def browser_tab_new(url: str, context: Context) -> str:
        service = TabsService(server_context)
        result = await service.create_new_tab(url)
        if not result["success"]:
            return f"Failed to open tab: {result['error']}"

        core_service = CoreService(server_context)
        url_result = await core_service.get_current_url()
        title_result = await core_service.get_page_title()

        current_url = url_result["data"]["url"] if url_result["success"] else "Unknown"
        page_title = (
            title_result["data"]["title"] if title_result["success"] else "Unknown"
        )

        return f"Successfully opened new tab\n URL: {current_url}\n Title: {page_title}\n Status: New tab created"

    @app.tool()
    async def browser_tab_close(tab_id: int, context: Context) -> str:
        service = TabsService(server_context)
        result = await service.close_tab(tab_id)
        return (
            f"Successfully closed tab {tab_id}"
            if result["success"]
            else f"Failed to close tab: {result['error']}"
        )

    @app.tool()
    async def browser_tab_select(tab_id: int, context: Context) -> str:
        service = TabsService(server_context)
        result = await service.select_tab(tab_id)
        if not result["success"]:
            return f"Failed to switch tab: {result['error']}"
        core_service = CoreService(server_context)
        url_result = await core_service.get_current_url()
        title_result = await core_service.get_page_title()

        current_url = url_result["data"]["url"] if url_result["success"] else "Unknown"
        page_title = (
            title_result["data"]["title"] if title_result["success"] else "Unknown"
        )

        return f"Successfully switched to tab {tab_id}\n URL: {current_url}\n Title: {page_title}\n Status: Tab switched"

    @app.tool()
    async def browser_tab_list(context: Context) -> str:
        service = TabsService(server_context)
        result = await service.list_tabs()
        if result["success"]:
            data = result["data"]
            result_text = f"Browser Tabs ({data['count']} total):\n\n"
            for tab in data["tabs"]:
                current_marker = "→ " if tab["is_current"] else "  "
                result_text += f"{current_marker}Tab {tab['index']}: {tab['title']}\n"
                result_text += f"   URL: {tab['url']}\n\n"
            return result_text
        else:
            return f"Failed to list tabs: {result['error']}"
