from typing import Dict, Any, TYPE_CHECKING
from core.tool_schema import (
    define_tool_factory,
    ToolCapability,
    ToolType,
    ToolResult,
    ToolActionResult,
    Tool,
    ToolSchema,
)
from core.schemas import EmptyInputSchema
from services.console_service import ConsoleService

if TYPE_CHECKING:
    from context import ServerContext


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
        service = ConsoleService(context)

        code = [
            "# Clear browser console messages",
            "# Removes all console entries",
        ]

        async def action() -> ToolActionResult:
            result = await service.clear_console()

            return ToolActionResult(
                content=[
                    {
                        "type": "text",
                        "text": result.message,
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
        service = ConsoleService(context)

        code = [
            "# Get browser console messages",
            "# Returns all console entries (log, warn, error, etc.)",
        ]

        async def action() -> ToolActionResult:
            result = await service.get_console_messages()

            if result.success:
                messages = result.data.get("messages", [])

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
            else:
                return ToolActionResult(
                    content=[
                        {
                            "type": "text",
                            "text": result.message,
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
