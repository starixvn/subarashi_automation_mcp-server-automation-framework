from typing import Dict, Any, TYPE_CHECKING
from core.tool_schema import (
    define_tool,
    ToolCapability,
    ToolType,
    ToolResult,
    ToolActionResult,
    Tool,
    ToolSchema,
)
from core.schemas import EmptyInputSchema

if TYPE_CHECKING:
    from ..context import ServerContext
    from ..services import SnapshotService


def _get_snapshot_service(context: "ServerContext") -> "SnapshotService":
    from services import SnapshotService

    return SnapshotService(context)


@define_tool(
    capability=ToolCapability.CORE,
    name="browser_snapshot",
    title="Page snapshot",
    description="Capture accessibility snapshot of the current page, this is better than screenshot",
    input_schema=EmptyInputSchema,
    tool_type=ToolType.READ_ONLY,
)
async def browser_snapshot(
    context: "ServerContext", params: Dict[str, Any]
) -> ToolResult:
    async def action() -> ToolActionResult:
        service = _get_snapshot_service(context)
        result = await service.capture_snapshot(include_screenshot=True)

        if result["success"]:
            data = result["data"]

            result_text = f"**Page Snapshot Captured**\n\n"
            result_text += f"**URL:** {data['url']}\n"
            result_text += f"**Title:** {data['title']}\n"
            result_text += f"**Elements Found:** {data['element_count']}\n"
            result_text += f"**Has Screenshot:** {data['has_screenshot']}\n\n"
            result_text += "**Accessibility Tree and Interactive Elements:**\n"
            result_text += data["snapshot_text"]

            return ToolActionResult(content=[{"type": "text", "text": result_text}])
        else:
            return ToolActionResult(
                content=[{"type": "text", "text": f"**Error**: {result['error']}"}]
            )

    return ToolResult(
        code=["# Capture accessibility snapshot of current page"],
        action=action,
        capture_snapshot=True,
        wait_for_network=False,
    )


def get_snapshot_tools(capture_snapshot: bool = True) -> list[Tool]:
    return [
        browser_snapshot,
    ]


SNAPSHOT_TOOLS = get_snapshot_tools()
