from typing import Dict, Any, TYPE_CHECKING
from .tool_schema import (
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
from .schemas import EmptyInputSchema, NavigateInputSchema, ResizeInputSchema

if TYPE_CHECKING:
    from ..context import ServerContext


@define_tool(
    capability=ToolCapability.CORE,
    name="browser_close",
    title="Close browser",
    description="Close the page",
    input_schema=EmptyInputSchema,
    tool_type=ToolType.READ_ONLY,
)
async def browser_close(context: "ServerContext", params: Dict[str, Any]) -> ToolResult:
    await context.close()
    
    return ToolResult(
        code=["await page.close()"],
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

        tab = await context.ensure_tab()
        await tab.navigate(validated_params.url)

        code = [
            f"// Navigate to {validated_params.url}",
            f"await page.goto('{validated_params.url}');",
        ]

        return ToolResult(
            code=code, capture_snapshot=capture_snapshot, wait_for_network=False
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

        tab = context.current_tab_or_die()

        code = [
            f"// Resize browser window to {validated_params.width}x{validated_params.height}",
            f"await page.setViewportSize({{ width: {validated_params.width}, height: {validated_params.height} }});",
        ]

        async def action() -> ToolActionResult:
            await tab.page.set_viewport_size(
                {"width": validated_params.width, "height": validated_params.height}
            )

        return ToolResult(
            code=code,
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
        tab = await context.ensure_tab()
        await tab.page.go_back()

        code = [
            "// Navigate back",
            "await page.goBack();",
        ]

        return ToolResult(
            code=code,
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
        tab = context.current_tab_or_die()
        await tab.page.go_forward()

        code = [
            "// Navigate forward",
            "await page.goForward();",
        ]

        return ToolResult(
            code=code,
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
