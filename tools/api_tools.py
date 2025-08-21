from mcp.server.fastmcp import FastMCP, Context
from context import ServerContext
from services import ApiService


def register_api_tools(app: FastMCP, server_context: ServerContext) -> None:
    @app.tool()
    async def api_request(
        method: str, url: str, context: Context, headers: str = "", body: str = ""
    ) -> str:
        service = ApiService(server_context)
        headers_dict = None
        if headers:
            try:
                import json

                headers_dict = (
                    json.loads(headers)
                    if headers.startswith("{")
                    else {
                        k.split(":")[0].strip(): k.split(":")[1].strip()
                        for k in headers.split(",")
                        if ":" in k
                    }
                )
            except Exception:
                headers_dict = {"Content-Type": "application/json"} if body else None

        result = await service.make_request(
            method, url, headers_dict, body if body else None
        )
        if result.success:
            response_data = result.data
            return f"API Request successful:\nStatus: {response_data['status']}\nResponse: {response_data.get('response_text', '')}"
        else:
            return f"API request failed: {result.error}"
