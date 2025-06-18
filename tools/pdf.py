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
from .schemas import SaveScreenshotInputSchema

if TYPE_CHECKING:
    from ..context import ServerContext


@define_tool_factory(
    capability=ToolCapability.PDF,
    name="browser_save_pdf",
    title="Save as PDF",
    description="Save current page as PDF",
    input_schema=SaveScreenshotInputSchema,
    tool_type=ToolType.READ_ONLY,
)
def browser_save_pdf_factory(capture_snapshot: bool) -> Tool:
    async def handle(context: "ServerContext", params: Dict[str, Any]) -> ToolResult:
        validated_params = SaveScreenshotInputSchema(**params)
        
        tab = context.current_tab_or_die()
        
        filename = validated_params.filename
        if not filename.endswith('.pdf'):
            filename += '.pdf'
        
        code = [
            f"// Save page as PDF: {filename}",
            f"await page.pdf({{ path: '{filename}', format: 'A4' }});",
        ]

        async def action() -> ToolActionResult:
            try:
                output_path = context.settings.output_dir / filename
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                await tab.page.pdf(
                    path=str(output_path),
                    format="A4",
                    print_background=True,
                    margin={
                        "top": "1cm",
                        "right": "1cm", 
                        "bottom": "1cm",
                        "left": "1cm"
                    }
                )
                
                return ToolActionResult(
                    content=[
                        {
                            "type": "text",
                            "text": f"PDF saved to {output_path}",
                        }
                    ]
                )
            except Exception as e:
                return ToolActionResult(
                    content=[
                        {
                            "type": "text",
                            "text": f"Failed to save PDF: {str(e)}",
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
        input_schema=SaveScreenshotInputSchema,
        tool_type=ToolType.READ_ONLY,
    )

    return Tool(capability=ToolCapability.PDF, schema=schema, handle=handle)


def get_pdf_tools(capture_snapshot: bool = True) -> list[Tool]:
    return [
        browser_save_pdf_factory(capture_snapshot),
    ] 

PDF_TOOLS = get_pdf_tools()