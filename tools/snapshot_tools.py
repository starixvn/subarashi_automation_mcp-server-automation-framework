from mcp.server.fastmcp import FastMCP, Context
from context import ServerContext
from services import SnapshotService
from mcp.types import TextContent


def register_snapshot_tools(app: FastMCP, server_context: ServerContext) -> None:
    @app.tool()
    async def browser_snapshot(context: Context) -> list[TextContent]:
        service = SnapshotService(server_context)
        result = await service.capture_snapshot_for_ai()

        if result["success"]:
            data = result["data"]
            result_text = "**AI Page Snapshot Captured**\n\n"
            result_text += f"**URL:** {data['url']}\n"
            result_text += f"**Title:** {data['title']}\n"
            result_text += f"**Elements Found:** {data['element_count']}\n"
            result_text += f"**Main Elements:** {data['main_elements_count']}\n"
            result_text += f"**Iframe Elements:** {data['iframe_elements_count']}\n"
            result_text += f"**Frames Processed:** {len(data['frames_processed'])}\n\n"
            result_text += "**AI Accessibility Tree with Iframe Recursion:**\n"
            result_text += data["snapshot_text"]

            return [TextContent(type="text", text=result_text)]
        else:
            return [TextContent(type="text", text=f"**Error**: {result['error']}")]
