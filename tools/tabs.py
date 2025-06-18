from typing import Dict, Any, TYPE_CHECKING
from .tool_schema import (
    define_tool,
    define_tool_factory,
    ToolCapability,
    ToolType,
    ToolResult,
    ToolActionResult,
    Tool,
    ToolSchema,
)
from .schemas import (
    EmptyInputSchema,
    NewTabInputSchema,
    SelectTabInputSchema,
    CloseTabInputSchema,
)

if TYPE_CHECKING:
    from ..context import ServerContext


def browser_tab_list_factory() -> Tool:

    async def handle(context: "ServerContext", params: Dict[str, Any]) -> ToolResult:
        await context.ensure_tab()

        code = ["// <internal code to list tabs>"]

        result_override = ToolActionResult(
            content=[
                {
                    "type": "text",
                    "text": await context.list_tabs_markdown(),
                }
            ]
        )

        return ToolResult(
            code=code,
            action=None,
            capture_snapshot=False,
            wait_for_network=False,
            result_override=result_override,
        )

    schema = ToolSchema(
        name="browser_tab_list",
        title="List tabs",
        description="List browser tabs",
        input_schema=EmptyInputSchema,
        tool_type=ToolType.READ_ONLY,
    )

    return Tool(capability=ToolCapability.TABS, schema=schema, handle=handle)


@define_tool_factory(
    capability=ToolCapability.TABS,
    name="browser_tab_select",
    title="Select a tab",
    description="Select a tab by index",
    input_schema=SelectTabInputSchema,
    tool_type=ToolType.READ_ONLY,
)
def browser_tab_select_factory(capture_snapshot: bool) -> Tool:

    async def handle(context: "ServerContext", params: Dict[str, Any]) -> ToolResult:
        validated_params = SelectTabInputSchema(**params)

        await context.select_tab(validated_params.index)

        code = [f"// <internal code to select tab {validated_params.index}>"]

        async def action() -> ToolActionResult:
            return ToolActionResult(
                content=[
                    {
                        "type": "text",
                        "text": f"Selected tab {validated_params.index}",
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
        name="browser_tab_select",
        title="Select a tab",
        description="Select a tab by index",
        input_schema=SelectTabInputSchema,
        tool_type=ToolType.READ_ONLY,
    )

    return Tool(capability=ToolCapability.TABS, schema=schema, handle=handle)


@define_tool_factory(
    capability=ToolCapability.TABS,
    name="browser_tab_new",
    title="Open a new tab",
    description="Open a new tab",
    input_schema=NewTabInputSchema,
    tool_type=ToolType.READ_ONLY,
)
def browser_tab_new_factory(capture_snapshot: bool) -> Tool:

    async def handle(context: "ServerContext", params: Dict[str, Any]) -> ToolResult:
        validated_params = NewTabInputSchema(**params)

        tab = await context.new_tab()

        if validated_params.url:
            await tab.navigate(validated_params.url)

        code = ["// <internal code to open a new tab>"]

        async def action() -> ToolActionResult:
            url_text = (
                f" and navigated to {validated_params.url}"
                if validated_params.url
                else ""
            )
            return ToolActionResult(
                content=[
                    {
                        "type": "text",
                        "text": f"Opened new tab{url_text}",
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
        name="browser_tab_new",
        title="Open a new tab",
        description="Open a new tab",
        input_schema=NewTabInputSchema,
        tool_type=ToolType.READ_ONLY,
    )

    return Tool(capability=ToolCapability.TABS, schema=schema, handle=handle)


@define_tool_factory(
    capability=ToolCapability.TABS,
    name="browser_tab_close",
    title="Close a tab",
    description="Close a tab",
    input_schema=CloseTabInputSchema,
    tool_type=ToolType.DESTRUCTIVE,
)
def browser_tab_close_factory(capture_snapshot: bool) -> Tool:

    async def handle(context: "ServerContext", params: Dict[str, Any]) -> ToolResult:
        validated_params = CloseTabInputSchema(**params)

        await context.close_tab(validated_params.index)

        code = [f"// <internal code to close tab {validated_params.index}>"]

        async def action() -> ToolActionResult:
            return ToolActionResult(
                content=[
                    {
                        "type": "text",
                        "text": f"Closed tab {validated_params.index if validated_params.index else 'current'}",
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
        name="browser_tab_close",
        title="Close a tab",
        description="Close a tab",
        input_schema=CloseTabInputSchema,
        tool_type=ToolType.DESTRUCTIVE,
    )

    return Tool(capability=ToolCapability.TABS, schema=schema, handle=handle)


def get_tab_tools(capture_snapshot: bool = True) -> list[Tool]:

    return [
        browser_tab_list_factory(),
        browser_tab_new_factory(capture_snapshot),
        browser_tab_select_factory(capture_snapshot),
        browser_tab_close_factory(capture_snapshot),
    ]


TAB_TOOLS = get_tab_tools()
