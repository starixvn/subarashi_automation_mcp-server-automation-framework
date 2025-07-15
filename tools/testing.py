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
from core.schemas import EmptyInputSchema
from services.testing_service import TestingService

if TYPE_CHECKING:
    from context import ServerContext


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
        service = TestingService(context)

        code = [
            "# Generate test code for current page",
            "# Creates Playwright test template",
        ]

        async def action() -> ToolActionResult:
            result = await service.generate_test()

            if result.success:
                return ToolActionResult(
                    content=[
                        {
                            "type": "text",
                            "text": f"Generated test:\n\n```typescript\n{result.data['test_code']}\n```",
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
