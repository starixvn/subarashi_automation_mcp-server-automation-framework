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
from core.schemas import UploadFileInputSchema
from services.files_service import FilesService

if TYPE_CHECKING:
    from ..context import ServerContext


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

        service = FilesService(context)

        code = [
            f"# Upload files to file chooser",
            f"# Files: {validated_params.file_paths}",
        ]

        async def action() -> ToolActionResult:
            result = await service.upload_files(validated_params.file_paths)

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
