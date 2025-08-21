from mcp.server.fastmcp import FastMCP, Context
from context import ServerContext
from services import NetworkService


def register_network_tools(app: FastMCP, server_context: ServerContext) -> None:
    @app.tool()
    async def browser_network_requests(context: Context) -> str:
        service = NetworkService(server_context)
        result = await service.get_network_requests()
        if result.success:
            requests = result.data["requests"]
            if not requests:
                return "No network requests captured"
            output = "Network Requests:\n\n"
            for req in requests:
                output += f"{req['method']} {req['url']}\n"
                output += f"Status: {req['status']}\n\n"
            return output
        else:
            return f"Failed to get requests: {result.error}"
