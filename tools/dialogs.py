from typing import Dict, Any, TYPE_CHECKING
from core.tool_schema import (
    define_tool_factory,
    ToolCapability,
    ToolType,
    ToolResult,
    ToolActionResult,
    Tool,
    ToolSchema,
    ModalStateType,
)
from core.schemas import DialogInputSchema
from services.dialogs_service import DialogsService

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

        service = DialogsService(context)

        code = [
            f"# Handle dialog",
            f"# Action: {'accept' if validated_params.accept else 'dismiss'}",
        ]

        if validated_params.accept and validated_params.prompt_text:
            code.append(f"# Prompt text: '{validated_params.prompt_text}'")

        async def action() -> ToolActionResult:
            result = await service.handle_dialog(
                validated_params.accept, validated_params.prompt_text
            )

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
        clears_modal_state="dialog",
    )


def get_dialog_tools(capture_snapshot: bool = True) -> list[Tool]:
    return [
        browser_handle_dialog_factory(capture_snapshot),
    ]


DIALOG_TOOLS = get_dialog_tools()
