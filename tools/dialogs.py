from typing import Dict, Any, TYPE_CHECKING
from .tool_schema import (
    define_tool_factory,
    ToolCapability,
    ToolType,
    ToolResult,
    ToolActionResult,
    Tool,
    ToolSchema,
    ModalStateType,
)
from .schemas import DialogInputSchema

if TYPE_CHECKING:
    from ..context import ServerContext


@define_tool_factory(
    capability=ToolCapability.CORE,
    name="browser_handle_dialog",
    title="Handle a dialog",
    description="Handle a dialog",
    input_schema=DialogInputSchema,
    tool_type=ToolType.DESTRUCTIVE,
)
def browser_handle_dialog_factory(capture_snapshot: bool) -> Tool:

    async def handle(context: "ServerContext", params: Dict[str, Any]) -> ToolResult:
        validated_params = DialogInputSchema(**params)

        dialog_state = None
        for state in context.modal_states():
            if state.type.value == "dialog":
                dialog_state = state
                break

        if not dialog_state:
            raise Exception("No dialog visible")

        if validated_params.accept:
            await dialog_state.dialog.accept(validated_params.prompt_text or "")
        else:
            await dialog_state.dialog.dismiss()

        context.clear_modal_state(dialog_state)

        code = [
            f'// <internal code to handle "{dialog_state.dialog.type}" dialog>',
        ]

        async def action() -> ToolActionResult:
            return ToolActionResult(
                content=[
                    {
                        "type": "text",
                        "text": f"Dialog {'accepted' if validated_params.accept else 'dismissed'}",
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
        name="browser_handle_dialog",
        title="Handle a dialog",
        description="Handle a dialog",
        input_schema=DialogInputSchema,
        tool_type=ToolType.DESTRUCTIVE,
    )

    return Tool(
        capability=ToolCapability.CORE,
        schema=schema,
        handle=handle,
        clears_modal_state="dialog",  # matches Playwright MCP's clearsModalState
    )


def get_dialog_tools(capture_snapshot: bool = True) -> list[Tool]:

    return [
        browser_handle_dialog_factory(capture_snapshot),
    ]


DIALOG_TOOLS = get_dialog_tools()