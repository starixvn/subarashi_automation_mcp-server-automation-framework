from mcp.server.fastmcp import FastMCP, Context
from context import ServerContext
from services import DialogsService


def register_dialog_tools(app: FastMCP, server_context: ServerContext) -> None:
    @app.tool(description="Handle a dialog")
    async def browser_handle_dialog(
        accept: bool, context: Context, prompt_text: str = ""
    ) -> str:
        service = DialogsService(server_context)
        result = await service.handle_dialog(
            accept, prompt_text if prompt_text else None
        )
        return (
            f"Dialog {'accepted' if accept else 'dismissed'} successfully"
            if result.success
            else f"Failed to handle dialog: {result.error}"
        )
