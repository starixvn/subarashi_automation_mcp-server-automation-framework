from typing import Dict, Any, TYPE_CHECKING
from .tool_schema import (
    define_tool_factory,
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


@define_tool_factory(
    capability=ToolCapability.CONSOLE,
    name="browser_console_clear",
    title="Clear console",
    description="Clear browser console messages",
    input_schema=EmptyInputSchema,
    tool_type=ToolType.READ_ONLY,
)
def browser_console_clear_factory(capture_snapshot: bool) -> Tool:
    async def handle(context: "ServerContext", params: Dict[str, Any]) -> ToolResult:
        tab = context.current_tab_or_die()
        
        code = [
            "// Clear console messages",
            "console.clear();",
        ]

        async def action() -> ToolActionResult:
            tab.clear_console_messages()
            return ToolActionResult(
                content=[
                    {
                        "type": "text",
                        "text": "Console messages cleared",
                    }
                ]
            )

        return ToolResult(
            code=code,
            action=action,
            capture_snapshot=capture_snapshot,
            wait_for_network=False,
        )

    schema = ToolSchema(
        name="browser_console_clear",
        title="Clear console",
        description="Clear browser console messages",
        input_schema=EmptyInputSchema,
        tool_type=ToolType.READ_ONLY,
    )

    return Tool(capability=ToolCapability.CONSOLE, schema=schema, handle=handle)


@define_tool_factory(
    capability=ToolCapability.CONSOLE,
    name="browser_console_messages",
    title="Get console messages",
    description="Get browser console messages",
    input_schema=EmptyInputSchema,
    tool_type=ToolType.READ_ONLY,
)
def browser_console_messages_factory(capture_snapshot: bool) -> Tool:
    async def handle(context: "ServerContext", params: Dict[str, Any]) -> ToolResult:
        tab = context.current_tab_or_die()
        
        code = ["// Get console messages"]

        async def action() -> ToolActionResult:
            messages = tab.get_console_messages()
            
            if not messages:
                return ToolActionResult(
                    content=[
                        {
                            "type": "text",
                            "text": "No console messages",
                        }
                    ]
                )

            lines = ["### Console Messages"]
            for msg in messages:
                lines.append(f"- **{msg['type']}**: {msg['text']}")
            
            return ToolActionResult(
                content=[
                    {
                        "type": "text",
                        "text": "\n".join(lines),
                    }
                ]
            )

        return ToolResult(
            code=code,
            action=action,
            capture_snapshot=capture_snapshot,
            wait_for_network=False,
        )

    schema = ToolSchema(
        name="browser_console_messages",
        title="Get console messages",
        description="Get browser console messages",
        input_schema=EmptyInputSchema,
        tool_type=ToolType.READ_ONLY,
    )

    return Tool(capability=ToolCapability.CONSOLE, schema=schema, handle=handle)


def get_console_tools(capture_snapshot: bool = True) -> list[Tool]:
    return [
        browser_console_clear_factory(capture_snapshot),
        browser_console_messages_factory(capture_snapshot),
    ] 

CONSOLE_TOOLS = get_console_tools()