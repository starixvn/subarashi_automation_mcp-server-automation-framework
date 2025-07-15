from typing import Dict, Any, TYPE_CHECKING
from core.tool_schema import (
    define_tool,
    define_tool_factory,
    ToolCapability,
    ToolType,
    ToolResult,
    ToolActionResult,
    ToolFactory,
    Tool,
    ToolSchema,
)
from core.schemas import EmptyInputSchema, NavigateInputSchema, ResizeInputSchema

if TYPE_CHECKING:
    from ..context import ServerContext
    from ..services import CoreService


def _get_core_service(context: "ServerContext") -> "CoreService":
    from services import CoreService

    return CoreService(context)


@define_tool(
    capability=ToolCapability.CORE,
    name="browser_close",
    title="Close browser",
    description="Close the page",
    input_schema=EmptyInputSchema,
    tool_type=ToolType.READ_ONLY,
)
async def browser_close(context: "ServerContext", params: Dict[str, Any]) -> ToolResult:
    async def action() -> ToolActionResult:
        service = _get_core_service(context)
        result = await service.close_browser()

        if result["success"]:
            return ToolActionResult(
                content=[{"type": "text", "text": result["message"]}]
            )
        else:
            return ToolActionResult(
                content=[{"type": "text", "text": f"Error: {result['error']}"}]
            )

    return ToolResult(
        code=["# Close browser"],
        action=action,
        capture_snapshot=False,
        wait_for_network=False,
    )


@define_tool_factory(
    capability=ToolCapability.CORE,
    name="browser_navigate",
    title="Navigate to a URL",
    description="Navigate to a URL",
    input_schema=NavigateInputSchema,
    tool_type=ToolType.DESTRUCTIVE,
)
def browser_navigate_factory(capture_snapshot: bool) -> "Tool":
    async def handle(context: "ServerContext", params: Dict[str, Any]) -> ToolResult:
        validated_params = NavigateInputSchema(**params)

        async def action() -> ToolActionResult:
            service = _get_core_service(context)
            result = await service.navigate_to_url(validated_params.url)

            if result["success"]:
                return ToolActionResult(
                    content=[
                        {
                            "type": "text",
                            "text": f"Successfully navigated to {result['data']['url']}",
                        }
                    ]
                )
            else:
                return ToolActionResult(
                    content=[
                        {
                            "type": "text",
                            "text": f"Navigation failed: {result['error']}",
                        }
                    ]
                )

        return ToolResult(
            code=[f"# Navigate to {validated_params.url}"],
            action=action,
            capture_snapshot=capture_snapshot,
            wait_for_network=False,
        )

    schema = ToolSchema(
        name="browser_navigate",
        title="Navigate to a URL",
        description="Navigate to a URL",
        input_schema=NavigateInputSchema,
        tool_type=ToolType.DESTRUCTIVE,
    )

    return Tool(capability=ToolCapability.CORE, schema=schema, handle=handle)


@define_tool_factory(
    capability=ToolCapability.CORE,
    name="browser_resize",
    title="Resize browser window",
    description="Resize the browser window",
    input_schema=ResizeInputSchema,
    tool_type=ToolType.READ_ONLY,
)
def browser_resize_factory(capture_snapshot: bool) -> "Tool":
    async def handle(context: "ServerContext", params: Dict[str, Any]) -> ToolResult:
        validated_params = ResizeInputSchema(**params)

        async def action() -> ToolActionResult:
            service = _get_core_service(context)
            result = await service.resize_browser(
                validated_params.width, validated_params.height
            )

            if result["success"]:
                return ToolActionResult(
                    content=[
                        {
                            "type": "text",
                            "text": f"Browser resized to {result['data']['width']}x{result['data']['height']}",
                        }
                    ]
                )
            else:
                return ToolActionResult(
                    content=[
                        {"type": "text", "text": f"Resize failed: {result['error']}"}
                    ]
                )

        return ToolResult(
            code=[
                f"# Resize browser to {validated_params.width}x{validated_params.height}"
            ],
            action=action,
            capture_snapshot=capture_snapshot,
            wait_for_network=True,
        )

    schema = ToolSchema(
        name="browser_resize",
        title="Resize browser window",
        description="Resize the browser window",
        input_schema=ResizeInputSchema,
        tool_type=ToolType.READ_ONLY,
    )

    return Tool(capability=ToolCapability.CORE, schema=schema, handle=handle)


@define_tool_factory(
    capability=ToolCapability.HISTORY,
    name="browser_navigate_back",
    title="Go back",
    description="Go back to the previous page",
    input_schema=EmptyInputSchema,
    tool_type=ToolType.READ_ONLY,
)
def browser_navigate_back_factory(capture_snapshot: bool) -> "Tool":
    async def handle(context: "ServerContext", params: Dict[str, Any]) -> ToolResult:
        async def action() -> ToolActionResult:
            service = _get_core_service(context)
            result = await service.go_back()

            if result["success"]:
                return ToolActionResult(
                    content=[
                        {
                            "type": "text",
                            "text": f"Navigated back to {result['data']['url']}",
                        }
                    ]
                )
            else:
                return ToolActionResult(
                    content=[
                        {"type": "text", "text": f"Go back failed: {result['error']}"}
                    ]
                )

        return ToolResult(
            code=["# Navigate back"],
            action=action,
            capture_snapshot=capture_snapshot,
            wait_for_network=False,
        )

    schema = ToolSchema(
        name="browser_navigate_back",
        title="Go back",
        description="Go back to the previous page",
        input_schema=EmptyInputSchema,
        tool_type=ToolType.READ_ONLY,
    )

    return Tool(capability=ToolCapability.HISTORY, schema=schema, handle=handle)


@define_tool_factory(
    capability=ToolCapability.HISTORY,
    name="browser_navigate_forward",
    title="Go forward",
    description="Go forward to the next page",
    input_schema=EmptyInputSchema,
    tool_type=ToolType.READ_ONLY,
)
def browser_navigate_forward_factory(capture_snapshot: bool) -> "Tool":
    async def handle(context: "ServerContext", params: Dict[str, Any]) -> ToolResult:
        async def action() -> ToolActionResult:
            service = _get_core_service(context)
            result = await service.go_forward()

            if result["success"]:
                return ToolActionResult(
                    content=[
                        {
                            "type": "text",
                            "text": f"Navigated forward to {result['data']['url']}",
                        }
                    ]
                )
            else:
                return ToolActionResult(
                    content=[
                        {
                            "type": "text",
                            "text": f"Go forward failed: {result['error']}",
                        }
                    ]
                )

        return ToolResult(
            code=["# Navigate forward"],
            action=action,
            capture_snapshot=capture_snapshot,
            wait_for_network=False,
        )

    schema = ToolSchema(
        name="browser_navigate_forward",
        title="Go forward",
        description="Go forward to the next page",
        input_schema=EmptyInputSchema,
        tool_type=ToolType.READ_ONLY,
    )

    return Tool(capability=ToolCapability.HISTORY, schema=schema, handle=handle)


def get_core_tools(capture_snapshot: bool = True) -> list["Tool"]:
    return [
        browser_close,
        browser_navigate_factory(capture_snapshot),
        browser_resize_factory(capture_snapshot),
        browser_navigate_back_factory(capture_snapshot),
        browser_navigate_forward_factory(capture_snapshot),
    ]


CORE_TOOLS = get_core_tools()
