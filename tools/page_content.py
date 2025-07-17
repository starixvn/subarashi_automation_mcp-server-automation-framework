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
from core.schemas import GetPageHtmlInputSchema, GetPageContentInputSchema

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


@define_tool_factory(
    capability=ToolCapability.CORE,
    name="browser_get_page_content",
    title="Get page content",
    description="Get structured page content including text, links, and metadata",
    input_schema=GetPageContentInputSchema,
    tool_type=ToolType.READ_ONLY,
)
def browser_get_page_content_factory(capture_snapshot: bool) -> Tool:
    async def handle(context: "ServerContext", params: Dict[str, Any]) -> ToolResult:
        validated_params = GetPageContentInputSchema(**params)

        async def action() -> ToolActionResult:
            service = _get_page_content_service(context)
            result = await service.get_page_content(
                include_meta=validated_params.include_meta,
                include_links=validated_params.include_links,
                include_images=validated_params.include_images,
                max_length=validated_params.max_length,
            )

            if result["success"]:
                data = result["data"]

                content_parts = [
                    f"**Page Title:** {data['title']}",
                    f"**Page URL:** {data['url']}",
                    "",
                    "**Page Text Content:**",
                    data["text"],
                ]

                if validated_params.include_meta and "meta" in data:
                    content_parts.extend(["", "**Meta Tags:**"])
                    for meta in data["meta"]:
                        content_parts.append(f"- {meta['name']}: {meta['content']}")

                if validated_params.include_links and "links" in data:
                    content_parts.extend(["", "**Links:**"])
                    for link in data["links"]:
                        content_parts.append(f"- [{link['text']}]({link['href']})")

                if validated_params.include_images and "images" in data:
                    content_parts.extend(["", "**Images:**"])
                    for img in data["images"]:
                        alt_text = f" (alt: {img['alt']})" if img["alt"] else ""
                        content_parts.append(f"- {img['src']}{alt_text}")

                result_text = "\n".join(content_parts)

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
            code=["# Extract structured page content for analysis"],
            action=action,
            capture_snapshot=False,
            wait_for_network=False,
        )

    schema = ToolSchema(
        name="browser_get_page_content",
        title="Get page content",
        description="Get structured page content including text, links, and metadata",
        input_schema=GetPageContentInputSchema,
        tool_type=ToolType.READ_ONLY,
    )

    return Tool(capability=ToolCapability.CORE, schema=schema, handle=handle)


def get_page_content_tools(capture_snapshot: bool = False) -> list[Tool]:
    return [
        browser_get_page_html_factory(capture_snapshot),
        browser_get_page_content_factory(capture_snapshot),
    ]


PAGE_CONTENT_TOOLS = get_page_content_tools(capture_snapshot=False)
