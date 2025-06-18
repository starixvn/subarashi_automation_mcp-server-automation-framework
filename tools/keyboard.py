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
from .schemas import PressKeyInputSchema

if TYPE_CHECKING:
    from ..context import ServerContext


@define_tool_factory(
    capability=ToolCapability.KEYBOARD,
    name="browser_press_key",
    title="Press key",
    description="Press a key on the keyboard",
    input_schema=PressKeyInputSchema,
    tool_type=ToolType.DESTRUCTIVE,
)
def browser_press_key_factory(capture_snapshot: bool) -> Tool:
    async def handle(context: "ServerContext", params: Dict[str, Any]) -> ToolResult:
        validated_params = PressKeyInputSchema(**params)
        
        tab = context.current_tab_or_die()
        
        code = [
            f"// Press key '{validated_params.key}'",
            f"await page.keyboard.press('{validated_params.key}');",
        ]

        async def action() -> ToolActionResult:
            try:
                await tab.page.keyboard.press(validated_params.key)
                return ToolActionResult(
                    content=[
                        {
                            "type": "text",
                            "text": f"Pressed key '{validated_params.key}'",
                        }
                    ]
                )
            except Exception as e:
                return ToolActionResult(
                    content=[
                        {
                            "type": "text",
                            "text": f"Failed to press key '{validated_params.key}': {str(e)}",
                        }
                    ]
                )

        return ToolResult(
            code=code,
            action=action,
            capture_snapshot=capture_snapshot,
            wait_for_network=True,
        )

    schema = ToolSchema(
        name="browser_press_key",
        title="Press key",
        description="Press a key on the keyboard",
        input_schema=PressKeyInputSchema,
        tool_type=ToolType.DESTRUCTIVE,
    )

    return Tool(capability=ToolCapability.KEYBOARD, schema=schema, handle=handle)


def get_keyboard_tools(capture_snapshot: bool = True) -> list[Tool]:
    return [
        browser_press_key_factory(capture_snapshot),
    ] 

KEYBOARD_TOOLS = get_keyboard_tools()