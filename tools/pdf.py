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
from core.schemas import PdfInputSchema
from services.pdf_service import PdfService

if TYPE_CHECKING:
    from context import ServerContext


@define_tool_factory(
    capability=ToolCapability.PDF,
    name="browser_save_pdf",
    title="Save as PDF",
    description="Save current page as PDF",
    input_schema=PdfInputSchema,
    tool_type=ToolType.READ_ONLY,
)
def browser_save_pdf_factory(capture_snapshot: bool) -> Tool:
    async def handle(context: "ServerContext", params: Dict[str, Any]) -> ToolResult:
        validated_params = PdfInputSchema(**params)

        service = PdfService(context)

        code = [
            f"# Save current page as PDF",
            f"# Filename: {validated_params.filename}",
            f"# Full page: {validated_params.full_page}",
        ]

        async def action() -> ToolActionResult:
            result = await service.save_as_pdf(
                validated_params.filename, validated_params.full_page
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
        name="browser_save_pdf",
        title="Save as PDF",
        description="Save current page as PDF",
        input_schema=PdfInputSchema,
        tool_type=ToolType.READ_ONLY,
    )

    return Tool(capability=ToolCapability.PDF, schema=schema, handle=handle)


def get_pdf_tools(capture_snapshot: bool = True) -> list[Tool]:
    return [
        browser_save_pdf_factory(capture_snapshot),
    ]


PDF_TOOLS = get_pdf_tools()
