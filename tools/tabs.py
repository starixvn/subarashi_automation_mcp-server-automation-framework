from typing import Dict, Any, TYPE_CHECKING
from core.tool_schema import (
    define_tool,
    define_tool_factory,
    ToolCapability,
    ToolType,
    ToolResult,
    ToolActionResult,
    Tool,
    ToolSchema,
)
from core.schemas import (
    EmptyInputSchema,
    NewTabInputSchema,
    SelectTabInputSchema,
    CloseTabInputSchema,
)

if TYPE_CHECKING:
    from ..context import ServerContext
    from ..services import TabsService


def _get_tabs_service(context: "ServerContext") -> "TabsService":
    from services import TabsService
    return TabsService(context)


def browser_tab_list_factory() -> Tool:
    
    async def handle(context: "ServerContext", params: Dict[str, Any]) -> ToolResult:
        
        async def action() -> ToolActionResult:
            service = _get_tabs_service(context)
            result = await service.list_tabs()
            
            if result["success"]:
                data = result["data"]
                
                result_text = f"**Browser Tabs ({data['count']} total):**\n\n"
                
                for tab in data["tabs"]:
                    current_marker = "→ " if tab["is_current"] else "  "
                    result_text += f"{current_marker}**Tab {tab['index']}:** {tab['title']}\n"
                    result_text += f"   URL: {tab['url']}\n\n"
                
                return ToolActionResult(
                    content=[{
                        "type": "text",
                        "text": result_text
                    }]
                )
            else:
                return ToolActionResult(
                    content=[{
                        "type": "text",
                        "text": f"Error listing tabs: {result['error']}"
                    }]
                )
        
        return ToolResult(
            code=["# List browser tabs"],
            action=action,
            capture_snapshot=False,
            wait_for_network=False,
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
        
        async def action() -> ToolActionResult:
            service = _get_tabs_service(context)
            result = await service.select_tab(validated_params.index)
            
            if result["success"]:
                data = result["data"]
                return ToolActionResult(
                    content=[{
                        "type": "text",
                        "text": f"Selected tab {data['index']}: {data['title']}\nURL: {data['url']}"
                    }]
                )
            else:
                return ToolActionResult(
                    content=[{
                        "type": "text",
                        "text": f"Failed to select tab: {result['error']}"
                    }]
                )
        
        return ToolResult(
            code=[f"# Select tab {validated_params.index}"],
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
        
        async def action() -> ToolActionResult:
            service = _get_tabs_service(context)
            result = await service.create_new_tab(validated_params.url)
            
            if result["success"]:
                data = result["data"]
                return ToolActionResult(
                    content=[{
                        "type": "text",
                        "text": f"Created new tab: {data['title']}\nURL: {data['url']}\nTotal tabs: {data['tab_count']}"
                    }]
                )
            else:
                return ToolActionResult(
                    content=[{
                        "type": "text",
                        "text": f"Failed to create new tab: {result['error']}"
                    }]
                )
        
        return ToolResult(
            code=["# Open new tab"],
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
        
        async def action() -> ToolActionResult:
            service = _get_tabs_service(context)
            result = await service.close_tab(validated_params.index)
            
            if result["success"]:
                data = result["data"]
                tab_description = f"tab {data['closed_index']}" if data['closed_index'] is not None else "current tab"
                return ToolActionResult(
                    content=[{
                        "type": "text",
                        "text": f"Closed {tab_description}\nRemaining tabs: {data['remaining_tabs']}"
                    }]
                )
            else:
                return ToolActionResult(
                    content=[{
                        "type": "text",
                        "text": f"Failed to close tab: {result['error']}"
                    }]
                )
        
        return ToolResult(
            code=[f"# Close tab {validated_params.index if validated_params.index else 'current'}"],
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
