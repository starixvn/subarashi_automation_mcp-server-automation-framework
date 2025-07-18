import re
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
from core.schemas import GetPageHtmlInputSchema

if TYPE_CHECKING:
    from ..context import ServerContext
    from ..services import PageContentService


def _get_page_content_service(context: "ServerContext") -> "PageContentService":
    from services import PageContentService

    return PageContentService(context)


@define_tool_factory(
    capability=ToolCapability.CORE,
    name="browser_get_page_html",
    title="Get page HTML",
    description="Get optimized page HTML for element mapping - removes scripts/styles but keeps all interactive elements",
    input_schema=GetPageHtmlInputSchema,
    tool_type=ToolType.READ_ONLY,
)
def browser_get_page_html_factory(capture_snapshot: bool) -> Tool:
    async def handle(context: "ServerContext", params: Dict[str, Any]) -> ToolResult:
        validated_params = GetPageHtmlInputSchema(**params)

        async def action() -> ToolActionResult:
            service = _get_page_content_service(context)
            result = await service.get_page_html(
                format_html=validated_params.format_html,
                max_length=validated_params.max_length,
            )

            if result["success"]:
                data = result["data"]
                info_msg = f"**Optimized HTML**: Removed scripts/styles | Original: {data['original_length']:,} chars"

                if data["truncated"]:
                    info_msg += f" | Shown: {data['shown_length']:,} chars (truncated)"
                else:
                    info_msg += f" | Length: {data['original_length']:,} characters"

                result_text = info_msg + "\n\n```html\n" + data["html"] + "\n```"

                return ToolActionResult(
                    content=[
                        {
                            "type": "text",
                            "text": result_text,
                        }
                    ]
                )
            else:
                return ToolActionResult(
                    content=[{"type": "text", "text": f"**Error**: {result['error']}"}]
                )

        return ToolResult(
            code=["# Get optimized page HTML for element mapping"],
            action=action,
            capture_snapshot=False,
            wait_for_network=False,
        )

    schema = ToolSchema(
        name="browser_get_page_html",
        title="Get page HTML",
        description="Get optimized page HTML for element mapping - removes unnecessary scripts/styles while preserving all interactive elements and their attributes",
        input_schema=GetPageHtmlInputSchema,
        tool_type=ToolType.READ_ONLY,
    )

    return Tool(capability=ToolCapability.CORE, schema=schema, handle=handle)


def get_page_content_tools(capture_snapshot: bool = False) -> list[Tool]:
    return [
        browser_get_page_html_factory(capture_snapshot),
    ]


PAGE_CONTENT_TOOLS = get_page_content_tools(capture_snapshot=False)
