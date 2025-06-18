from typing import Dict, Any, TYPE_CHECKING
from .tool_schema import (
    define_tool,
    ToolCapability,
    ToolType,
    ToolResult,
    ToolActionResult,
    Tool,
    ToolSchema,
)
from .schemas import EmptyInputSchema

if TYPE_CHECKING:
    from ..context import ServerContext


@define_tool(
    capability=ToolCapability.CORE,
    name="browser_snapshot",
    title="Page snapshot", 
    description="Capture accessibility snapshot of the current page, this is better than screenshot",
    input_schema=EmptyInputSchema,
    tool_type=ToolType.READ_ONLY,
)
async def browser_snapshot(context: "ServerContext", params: Dict[str, Any]) -> ToolResult:
    await context.ensure_tab()
    
    return ToolResult(
        code=["// <internal code to capture accessibility snapshot>"],
        capture_snapshot=True,
        wait_for_network=False,
    )


def get_snapshot_tools(capture_snapshot: bool = True) -> list[Tool]:
    """Snapshot tools that match TypeScript snapshot.ts export"""
    return [
        browser_snapshot,
    ] 

SNAPSHOT_TOOLS = get_snapshot_tools()