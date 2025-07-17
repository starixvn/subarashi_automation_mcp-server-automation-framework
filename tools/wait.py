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
    WaitForInputSchema,
    WaitForSelectorInputSchema,
)
from services.wait_service import WaitService

if TYPE_CHECKING:
    from context import ServerContext


@define_tool_factory(
    capability=ToolCapability.WAIT,
    name="browser_wait_for",
    title="Wait for condition",
    description="Wait for time, text, or text to disappear",
    input_schema=WaitForInputSchema,
    tool_type=ToolType.READ_ONLY,
)
def browser_wait_for_factory(capture_snapshot: bool) -> Tool:
    async def handle(context: "ServerContext", params: Dict[str, Any]) -> ToolResult:
        validated_params = WaitForInputSchema(**params)

        service = WaitService(context)

        code = []
        wait_actions = []

        if validated_params.time:
            code.append(f"# Wait for {validated_params.time} seconds")
            wait_actions.append(("time", validated_params.time))

        if validated_params.text:
            code.append(f"# Wait for text '{validated_params.text}' to appear")
            wait_actions.append(("text", validated_params.text))
        if validated_params.text_gone:
            code.append(f"# Wait for text '{validated_params.text_gone}' to disappear")
            wait_actions.append(("text_gone", validated_params.text_gone))

        async def action() -> ToolActionResult:
            try:
                results = []

                for action_type, value in wait_actions:
                    if action_type == "time":
                        result = await service.wait_for_timeout(value)
                    elif action_type == "text":
                        result = await service.wait_for_text(value)
                    elif action_type == "text_gone":
                        result = await service.wait_for_text_gone(value)

                    results.append(result)

                    if not result.success:
                        return ToolActionResult(
                            content=[
                                {
                                    "type": "text",
                                    "text": result.message,
                                }
                            ]
                        )

                conditions = []
                if validated_params.time:
                    conditions.append(f"{validated_params.time} seconds")
                if validated_params.text:
                    conditions.append(f"text '{validated_params.text}'")
                if validated_params.text_gone:
                    conditions.append(
                        f"text '{validated_params.text_gone}' to disappear"
                    )

                return ToolActionResult(
                    content=[
                        {
                            "type": "text",
                            "text": f"Waited for: {', '.join(conditions)}",
                        }
                    ]
                )
            except Exception as e:
                return ToolActionResult(
                    content=[
                        {
                            "type": "text",
                            "text": f"Wait failed: {str(e)}",
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
        name="browser_wait_for",
        title="Wait for condition",
        description="Wait for time, text, or text to disappear",
        input_schema=WaitForInputSchema,
        tool_type=ToolType.READ_ONLY,
    )

    return Tool(capability=ToolCapability.WAIT, schema=schema, handle=handle)


@define_tool_factory(
    capability=ToolCapability.WAIT,
    name="browser_wait_for_selector",
    title="Wait for selector",
    description="Wait for element to appear",
    input_schema=WaitForSelectorInputSchema,
    tool_type=ToolType.READ_ONLY,
)
def browser_wait_for_selector_factory(capture_snapshot: bool) -> Tool:
    async def handle(context: "ServerContext", params: Dict[str, Any]) -> ToolResult:
        validated_params = WaitForSelectorInputSchema(**params)

        service = WaitService(context)

        code = [
            f"# Wait for element to appear",
            f"# Selector: '{validated_params.selector}'",
            f"# Timeout: {validated_params.timeout} seconds",
        ]

        async def action() -> ToolActionResult:
            result = await service.wait_for_selector(
                validated_params.selector, validated_params.timeout
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
        name="browser_wait_for_selector",
        title="Wait for selector",
        description="Wait for element to appear",
        input_schema=WaitForSelectorInputSchema,
        tool_type=ToolType.READ_ONLY,
    )

    return Tool(capability=ToolCapability.WAIT, schema=schema, handle=handle)


def get_wait_tools(capture_snapshot: bool = True) -> list[Tool]:
    return [
        browser_wait_for_factory(capture_snapshot),
        browser_wait_for_selector_factory(capture_snapshot),
    ]


WAIT_TOOLS = get_wait_tools()
