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
    WaitForInputSchema,
    WaitForSelectorInputSchema,
)

if TYPE_CHECKING:
    from ..context import ServerContext


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
        
        tab = context.current_tab_or_die()
        
        code = []
        actions = []
        
        if validated_params.time:
            code.append(f"// Wait for {validated_params.time} seconds")
            code.append(f"await page.waitForTimeout({int(validated_params.time * 1000)});")
            actions.append(lambda: context.wait_for_timeout(validated_params.time))
        
        if validated_params.text:
            code.append(f"// Wait for text '{validated_params.text}' to appear")
            code.append(f"await page.waitForFunction(() => document.body.innerText.includes('{validated_params.text}'));")
            actions.append(lambda: tab.page.wait_for_function(
                f"() => document.body.innerText.includes('{validated_params.text}')"
            ))
        
        if validated_params.text_gone:
            code.append(f"// Wait for text '{validated_params.text_gone}' to disappear")
            code.append(f"await page.waitForFunction(() => !document.body.innerText.includes('{validated_params.text_gone}'));")
            actions.append(lambda: tab.page.wait_for_function(
                f"() => !document.body.innerText.includes('{validated_params.text_gone}')"
            ))

        async def action() -> ToolActionResult:
            try:
                for wait_action in actions:
                    await wait_action()
                
                conditions = []
                if validated_params.time:
                    conditions.append(f"{validated_params.time} seconds")
                if validated_params.text:
                    conditions.append(f"text '{validated_params.text}'")
                if validated_params.text_gone:
                    conditions.append(f"text '{validated_params.text_gone}' to disappear")
                
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
        
        tab = context.current_tab_or_die()
        
        code = [
            f"// Wait for selector '{validated_params.selector}'",
            f"await page.waitForSelector('{validated_params.selector}', {{ timeout: {int(validated_params.timeout * 1000)} }});",
        ]

        async def action() -> ToolActionResult:
            try:
                await tab.page.wait_for_selector(
                    validated_params.selector,
                    timeout=int(validated_params.timeout * 1000)
                )
                
                return ToolActionResult(
                    content=[
                        {
                            "type": "text",
                            "text": f"Element '{validated_params.selector}' appeared",
                        }
                    ]
                )
            except Exception as e:
                return ToolActionResult(
                    content=[
                        {
                            "type": "text",
                            "text": f"Wait for selector failed: {str(e)}",
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