from mcp.server.fastmcp import FastMCP, Context
from context import ServerContext
from services import FilesService


def register_files_tools(app: FastMCP, server_context: ServerContext) -> None:
    @app.tool(description="Upload files to the browser")
    async def browser_upload_files(file_paths: str, context: Context) -> str:
        service = FilesService(server_context)
        file_list = [fp.strip() for fp in file_paths.split(",")]
        result = await service.upload_files(file_list)
        return (
            f"Successfully uploaded files: {', '.join(file_list)}"
            if result.success
            else f"Failed to upload files: {result.error}"
        )
