from mcp.server.fastmcp import FastMCP, Context
from context import ServerContext
from services import KeyboardService


def register_keyboard_tools(app: FastMCP, server_context: ServerContext) -> None:
    @app.tool()
    async def browser_press_key(key: str, context: Context) -> str:
        service = KeyboardService(server_context)
        result = await service.press_key(key)
        return (
            f"Successfully pressed key '{key}'"
            if result.success
            else f"Failed to press key: {result.error}"
        )
