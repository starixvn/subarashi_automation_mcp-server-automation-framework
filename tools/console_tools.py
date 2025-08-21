from mcp.server.fastmcp import FastMCP, Context
from context import ServerContext
from services import ConsoleService


def register_console_tools(app: FastMCP, server_context: ServerContext) -> None:
    @app.tool()
    async def browser_console_clear(context: Context) -> str:
        service = ConsoleService(server_context)
        result = await service.clear_console()
        return (
            "Console cleared successfully"
            if result.success
            else f"Failed to clear console: {result.error}"
        )

    @app.tool()
    async def browser_console_messages(context: Context) -> str:
        service = ConsoleService(server_context)
        result = await service.get_console_messages()
        if result.success:
            messages = result.data["messages"]
            if not messages:
                return "No console messages"
            output = "Console Messages:\n\n"
            for msg in messages:
                output += f"[{msg['type'].upper()}] {msg['text']}\n"
            return output
        else:
            return f"Failed to get console messages: {result.error}"
