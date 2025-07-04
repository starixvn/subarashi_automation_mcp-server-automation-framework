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
from .schemas import UploadFileInputSchema

if TYPE_CHECKING:
    from ..context import ServerContext
    from ..core.modal_state import FileChooserModalState


@define_tool_factory(
    capability=ToolCapability.FILES,
    name="browser_upload_file",
    title="Upload file",
    description="Upload file to file chooser",
    input_schema=UploadFileInputSchema,
    tool_type=ToolType.DESTRUCTIVE,
    clears_modal_state="fileChooser",
)
def browser_upload_file_factory(capture_snapshot: bool) -> Tool:
    async def handle(context: "ServerContext", params: Dict[str, Any]) -> ToolResult:
        validated_params = UploadFileInputSchema(**params)

        file_chooser_state = None
        for state in context.modal_states():
            if state.type.value == "fileChooser":
                file_chooser_state = state
                break

        if not file_chooser_state:
            raise Exception("No file chooser visible")

        code = [
            f"// Upload files: {validated_params.file_paths}",
            f"await fileChooser.setFiles({validated_params.file_paths});",
        ]

        async def action() -> ToolActionResult:
            try:
                
                fc_state = file_chooser_state
                if isinstance(fc_state, FileChooserModalState):
                    await fc_state.file_chooser.set_files(validated_params.file_paths)
                context.clear_modal_state(file_chooser_state)
                
                return ToolActionResult(
                    content=[
                        {
                            "type": "text",
                            "text": f"Uploaded files: {validated_params.file_paths}",
                        }
                    ]
                )
            except Exception as e:
                return ToolActionResult(
                    content=[
                        {
                            "type": "text",
                            "text": f"Failed to upload files: {str(e)}",
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
        name="browser_upload_file",
        title="Upload file",
        description="Upload file to file chooser",
        input_schema=UploadFileInputSchema,
        tool_type=ToolType.DESTRUCTIVE,
    )

    return Tool(
        capability=ToolCapability.FILES,
        schema=schema,
        handle=handle,
        clears_modal_state="fileChooser",
    )


def get_file_tools(capture_snapshot: bool = True) -> list[Tool]:
    return [
        browser_upload_file_factory(capture_snapshot),
    ] 

FILE_TOOLS = get_file_tools()