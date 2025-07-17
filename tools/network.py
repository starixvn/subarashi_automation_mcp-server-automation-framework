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
from core.schemas import (
    EmptyInputSchema,
    SetRequestInterceptionInputSchema,
)
from services.network_service import NetworkService

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
        service = NetworkService(context)

        # Python implementation comments
        code = [
            "# Get network requests from current tab",
            "# Returns list of HTTP requests made by the page",
        ]

        async def action() -> ToolActionResult:
            result = await service.get_network_requests()

            if result.success:
                requests = result.data.get("requests", [])
                if not requests:
                    return ToolActionResult(
                        content=[
                            {
                                "type": "text",
                                "text": "No network requests",
                            }
                        ]
                    )

                # Format requests for display
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
            else:
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

        service = NetworkService(context)

        # Python implementation comments
        code = [
            f"# Set request interception",
            f"# Enabled: {validated_params.enabled}",
        ]

        if validated_params.enabled and validated_params.patterns:
            code.append(f"# Patterns: {validated_params.patterns}")

        async def action() -> ToolActionResult:
            result = await service.set_request_interception(
                validated_params.enabled, validated_params.patterns
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
