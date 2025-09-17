from mcp.server.fastmcp import FastMCP, Context
from context import ServerContext
from services import PageContentService
from services import CoreService


def register_evaluate_tools(app: FastMCP, server_context: ServerContext) -> None:
    @app.tool(description="Evaluate JavaScript code in the browser")
    async def browser_evaluate(javascript_code: str, context: Context) -> str:
        service = PageContentService(server_context)
        result = await service.evaluate_javascript(javascript_code)
        if not result["success"]:
            return f"JavaScript evaluation failed: {result['error']}"

        core_service = CoreService(server_context)
        url_result = await core_service.get_current_url()
        title_result = await core_service.get_page_title()

        current_url = url_result["data"]["url"] if url_result["success"] else "Unknown"
        page_title = (
            title_result["data"]["title"] if title_result["success"] else "Unknown"
        )
        js_result = str(result["data"]["result"])

        return f"JavaScript executed:\n URL: {current_url}\n Title: {page_title}\n Result: {js_result}\n Status: JavaScript evaluation completed"
