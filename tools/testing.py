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
from .schemas import EmptyInputSchema

if TYPE_CHECKING:
    from ..context import ServerContext


@define_tool_factory(
    capability=ToolCapability.TESTING,
    name="browser_generate_test",
    title="Generate test",
    description="Generate test code for current page state",
    input_schema=EmptyInputSchema,
    tool_type=ToolType.READ_ONLY,
)
def browser_generate_test_factory(capture_snapshot: bool) -> Tool:
    async def handle(context: "ServerContext", params: Dict[str, Any]) -> ToolResult:
        tab = context.current_tab_or_die()
        
        code = ["// Generate test for current page state"]

        async def action() -> ToolActionResult:
            try:
                url = tab.url()
                title = await tab.title()
                
                test_code = [
                    "import { test, expect } from '@playwright/test';",
                    "",
                    f"test('Test for {title}', async ({{ page }}) => {{",
                    f"  await page.goto('{url}');",
                    f"  await expect(page).toHaveTitle('{title}');",
                    "});",
                ]
                
                return ToolActionResult(
                    content=[
                        {
                            "type": "text",
                            "text": f"Generated test:\n\n```typescript\n" + "\n".join(test_code) + "\n```",
                        }
                    ]
                )
            except Exception as e:
                return ToolActionResult(
                    content=[
                        {
                            "type": "text",
                            "text": f"Failed to generate test: {str(e)}",
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
        name="browser_generate_test",
        title="Generate test",
        description="Generate test code for current page state",
        input_schema=EmptyInputSchema,
        tool_type=ToolType.READ_ONLY,
    )

    return Tool(capability=ToolCapability.TESTING, schema=schema, handle=handle)


def get_testing_tools(capture_snapshot: bool = True) -> list[Tool]:
    return [
        browser_generate_test_factory(capture_snapshot),
    ] 

TESTING_TOOLS = get_testing_tools()