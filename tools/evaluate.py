from typing import Dict, Any, Optional, TYPE_CHECKING
from core.tool_schema import (
    define_tool_factory,
    ToolCapability,
    ToolType,
    ToolResult,
    ToolActionResult,
    Tool,
    ToolSchema,
)
from core.schemas import EvaluateJavaScriptInputSchema
import json

if TYPE_CHECKING:
    from ..context import ServerContext
    from ..services import PageContentService


def _get_page_content_service(context: "ServerContext") -> "PageContentService":
    from services import PageContentService

    return PageContentService(context)


@define_tool_factory(
    capability=ToolCapability.CORE,
    name="browser_evaluate",
    title="Evaluate JavaScript",
    description="Evaluate JavaScript expression on page or element",
    input_schema=EvaluateJavaScriptInputSchema,
    tool_type=ToolType.DESTRUCTIVE,
)
def browser_evaluate_factory(capture_snapshot: bool) -> Tool:
    async def handle(context: "ServerContext", params: Dict[str, Any]) -> ToolResult:
        validated_params = EvaluateJavaScriptInputSchema(**params)

        service = _get_page_content_service(context)

        element_ref = None
        if validated_params.ref and validated_params.element:
            element_ref = {
                "element": validated_params.element,
                "ref": validated_params.ref,
            }

        code = []
        if element_ref:
            code.append(f"# Evaluate JavaScript on element: {validated_params.element}")
            code.append(f"# Function: {validated_params.function}")
        else:
            code.append(f"# Evaluate JavaScript on page")
            code.append(f"# Function: {validated_params.function}")

        async def action() -> ToolActionResult:
            result = await service.evaluate_javascript(
                validated_params.function, element_ref
            )

            if result["success"]:
                return ToolActionResult(
                    content=[
                        {
                            "type": "text",
                            "text": "Result: "
                            + (
                                json.dumps(result["data"]["result"], indent=2)
                                if result["data"]["result"] is not None
                                else "undefined"
                            ),
                        }
                    ]
                )
            else:
                return ToolActionResult(
                    content=[{"type": "text", "text": f"Error: {result['error']}"}]
                )

        return ToolResult(
            code=code,
            action=action,
            capture_snapshot=capture_snapshot,
            wait_for_network=False,
        )

    schema = ToolSchema(
        name="browser_evaluate",
        title="Evaluate JavaScript",
        description="Evaluate JavaScript expression on page or element",
        input_schema=EvaluateJavaScriptInputSchema,
        tool_type=ToolType.DESTRUCTIVE,
    )

    return Tool(capability=ToolCapability.CORE, schema=schema, handle=handle)


def get_evaluate_tools(capture_snapshot: bool = False) -> list[Tool]:
    return [
        browser_evaluate_factory(capture_snapshot),
    ]


EVALUATE_TOOLS = get_evaluate_tools()
