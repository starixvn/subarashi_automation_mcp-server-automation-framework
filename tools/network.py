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
from .schemas import (
    EmptyInputSchema,
    SetRequestInterceptionInputSchema,
)

if TYPE_CHECKING:
    from ..context import ServerContext


@define_tool_factory(
    capability=ToolCapability.NETWORK,
    name="browser_network_requests",
    title="Get network requests",
    description="Get network requests from current tab",
    input_schema=EmptyInputSchema,
    tool_type=ToolType.READ_ONLY,
)
def browser_network_requests_factory(capture_snapshot: bool) -> Tool:
    async def handle(context: "ServerContext", params: Dict[str, Any]) -> ToolResult:
        tab = context.current_tab_or_die()
        
        code = ["// Get network requests"]

        async def action() -> ToolActionResult:
            requests = tab.get_network_requests()
            
            if not requests:
                return ToolActionResult(
                    content=[
                        {
                            "type": "text",
                            "text": "No network requests",
                        }
                    ]
                )

            lines = ["### Network Requests"]
            for req in requests:
                method = req.get("method", "GET")
                url = req.get("url", "")
                lines.append(f"- **{method}** {url}")
            
            return ToolActionResult(
                content=[
                    {
                        "type": "text",
                        "text": "\n".join(lines),
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
        name="browser_network_requests",
        title="Get network requests",
        description="Get network requests from current tab",
        input_schema=EmptyInputSchema,
        tool_type=ToolType.READ_ONLY,
    )

    return Tool(capability=ToolCapability.NETWORK, schema=schema, handle=handle)


@define_tool_factory(
    capability=ToolCapability.NETWORK,
    name="browser_set_request_interception",
    title="Set request interception",
    description="Enable or disable request interception",
    input_schema=SetRequestInterceptionInputSchema,
    tool_type=ToolType.DESTRUCTIVE,
)
def browser_set_request_interception_factory(capture_snapshot: bool) -> Tool:
    async def handle(context: "ServerContext", params: Dict[str, Any]) -> ToolResult:
        validated_params = SetRequestInterceptionInputSchema(**params)
        
        tab = context.current_tab_or_die()
        
        code = [
            f"// Set request interception: {validated_params.enabled}",
            f"await page.route('**/*', route => route.continue());",
        ]

        async def action() -> ToolActionResult:
            try:
                if validated_params.enabled:
                    patterns = validated_params.patterns or ["**/*"]
                    for pattern in patterns:
                        await tab.page.route(pattern, lambda route: route.continue_())
                    
                    return ToolActionResult(
                        content=[
                            {
                                "type": "text",
                                "text": f"Request interception enabled for patterns: {patterns}",
                            }
                        ]
                    )
                else:
                    await tab.page.unroute("**/*")
                    return ToolActionResult(
                        content=[
                            {
                                "type": "text",
                                "text": "Request interception disabled",
                            }
                        ]
                    )
            except Exception as e:
                return ToolActionResult(
                    content=[
                        {
                            "type": "text",
                            "text": f"Failed to set request interception: {str(e)}",
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
        name="browser_set_request_interception",
        title="Set request interception",
        description="Enable or disable request interception",
        input_schema=SetRequestInterceptionInputSchema,
        tool_type=ToolType.DESTRUCTIVE,
    )

    return Tool(capability=ToolCapability.NETWORK, schema=schema, handle=handle)


def get_network_tools(capture_snapshot: bool = True) -> list[Tool]:
    return [
        browser_network_requests_factory(capture_snapshot),
        browser_set_request_interception_factory(capture_snapshot),
    ] 

NETWORK_TOOLS = get_network_tools()