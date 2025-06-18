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
    ScreenshotInputSchema,
    SaveScreenshotInputSchema,
    ScreenClickInputSchema,
    ScreenDragInputSchema,
    ScreenTypeInputSchema,
    ScreenMoveMouseInputSchema,
    EmptyInputSchema,
)

if TYPE_CHECKING:
    from ..context import ServerContext


@define_tool_factory(
    capability=ToolCapability.VISION,
    name="browser_screenshot",
    title="Take screenshot",
    description="Take a screenshot of the current page",
    input_schema=ScreenshotInputSchema,
    tool_type=ToolType.READ_ONLY,
)
def browser_screenshot_factory(capture_snapshot: bool) -> Tool:

    async def handle(context: "ServerContext", params: Dict[str, Any]) -> ToolResult:
        validated_params = ScreenshotInputSchema(**params)

        tab = context.current_tab_or_die()

        code = [
            f"// Take screenshot (full_page={validated_params.full_page})",
            f"await page.screenshot({{ fullPage: {str(validated_params.full_page).lower()} }});",
        ]

        async def action() -> ToolActionResult:
            try:
                snapshot = await tab.capture_snapshot(include_screenshot=True)

                content = [
                    {"type": "text", "text": f"Screenshot taken of {snapshot.url()}"}
                ]

                if context.client_supports_images() and snapshot.has_screenshot():
                    import base64

                    screenshot_data = snapshot.get_screenshot_data()
                    if screenshot_data:
                        content.append(
                            {
                                "type": "image",
                                "data": base64.b64encode(screenshot_data).decode(),
                                "mimeType": "image/png",
                            }
                        )

                return ToolActionResult(content=content)

            except Exception as e:
                return ToolActionResult(
                    content=[
                        {"type": "text", "text": f"Failed to take screenshot: {str(e)}"}
                    ]
                )

        return ToolResult(
            code=code,
            action=action,
            capture_snapshot=capture_snapshot,
            wait_for_network=False,
        )

    schema = ToolSchema(
        name="browser_screenshot",
        title="Take screenshot",
        description="Take a screenshot of the current page",
        input_schema=ScreenshotInputSchema,
        tool_type=ToolType.READ_ONLY,
    )

    return Tool(capability=ToolCapability.VISION, schema=schema, handle=handle)


@define_tool_factory(
    capability=ToolCapability.VISION,
    name="browser_save_screenshot",
    title="Save screenshot",
    description="Save a screenshot to file",
    input_schema=SaveScreenshotInputSchema,
    tool_type=ToolType.READ_ONLY,
)
def browser_save_screenshot_factory(capture_snapshot: bool) -> Tool:

    async def handle(context: "ServerContext", params: Dict[str, Any]) -> ToolResult:
        validated_params = SaveScreenshotInputSchema(**params)

        tab = context.current_tab_or_die()

        code = [
            f"// Save screenshot to {validated_params.filename}",
            f"await page.screenshot({{ path: '{validated_params.filename}', fullPage: {str(validated_params.full_page).lower()} }});",
        ]

        async def action() -> ToolActionResult:
            try:
                snapshot = await tab.capture_snapshot(include_screenshot=True)

                output_path = context.settings.output_dir / validated_params.filename
                success = await snapshot.save_screenshot(output_path)

                if success:
                    return ToolActionResult(
                        content=[
                            {
                                "type": "text",
                                "text": f"Screenshot saved to {output_path}",
                            }
                        ]
                    )
                else:
                    return ToolActionResult(
                        content=[
                            {
                                "type": "text",
                                "text": f"Failed to save screenshot to {output_path}",
                            }
                        ]
                    )

            except Exception as e:
                return ToolActionResult(
                    content=[
                        {"type": "text", "text": f"Failed to save screenshot: {str(e)}"}
                    ]
                )

        return ToolResult(
            code=code,
            action=action,
            capture_snapshot=capture_snapshot,
            wait_for_network=False,
        )

    schema = ToolSchema(
        name="browser_save_screenshot",
        title="Save screenshot",
        description="Save a screenshot to file",
        input_schema=SaveScreenshotInputSchema,
        tool_type=ToolType.READ_ONLY,
    )

    return Tool(capability=ToolCapability.VISION, schema=schema, handle=handle)


@define_tool_factory(
    capability=ToolCapability.VISION,
    name="browser_screen_click",
    title="Click at coordinates",
    description="Click at specific screen coordinates",
    input_schema=ScreenClickInputSchema,
    tool_type=ToolType.DESTRUCTIVE,
)
def browser_screen_click_factory(capture_snapshot: bool) -> Tool:

    async def handle(context: "ServerContext", params: Dict[str, Any]) -> ToolResult:
        validated_params = ScreenClickInputSchema(**params)

        tab = context.current_tab_or_die()

        code = [
            f"// Click at coordinates ({validated_params.x}, {validated_params.y}) - {validated_params.element}",
            f"await page.mouse.click({validated_params.x}, {validated_params.y});",
        ]

        async def action() -> ToolActionResult:
            try:
                await tab.page.mouse.click(validated_params.x, validated_params.y)

                return ToolActionResult(
                    content=[
                        {
                            "type": "text",
                            "text": f"Clicked at coordinates ({validated_params.x}, {validated_params.y}) - {validated_params.element}",
                        }
                    ]
                )

            except Exception as e:
                return ToolActionResult(
                    content=[
                        {
                            "type": "text",
                            "text": f"Failed to click at coordinates: {str(e)}",
                        }
                    ]
                )

        return ToolResult(
            code=code,
            action=action,
            capture_snapshot=capture_snapshot,
            wait_for_network=True,
        )

    schema = ToolSchema(
        name="browser_screen_click",
        title="Click at coordinates",
        description="Click at specific screen coordinates",
        input_schema=ScreenClickInputSchema,
        tool_type=ToolType.DESTRUCTIVE,
    )

    return Tool(capability=ToolCapability.VISION, schema=schema, handle=handle)


@define_tool_factory(
    capability=ToolCapability.VISION,
    name="browser_capture_snapshot",
    title="Capture page snapshot",
    description="Capture accessibility snapshot of the current page",
    input_schema=EmptyInputSchema,
    tool_type=ToolType.READ_ONLY,
)
def browser_capture_snapshot_factory(capture_snapshot: bool) -> Tool:

    async def handle(context: "ServerContext", params: Dict[str, Any]) -> ToolResult:
        tab = context.current_tab_or_die()

        code = [
            "// Capture page snapshot with accessibility tree",
            "const snapshot = await page.accessibility.snapshot({ interestingOnly: true });",
        ]

        async def action() -> ToolActionResult:
            try:
                snapshot = await tab.capture_snapshot(
                    include_screenshot=capture_snapshot
                )

                return ToolActionResult(
                    content=[{"type": "text", "text": snapshot.text()}]
                )

            except Exception as e:
                return ToolActionResult(
                    content=[
                        {
                            "type": "text",
                            "text": f"Failed to capture snapshot: {str(e)}",
                        }
                    ]
                )

        return ToolResult(
            code=code,
            action=action,
            capture_snapshot=False,
            wait_for_network=False,
        )

    schema = ToolSchema(
        name="browser_capture_snapshot",
        title="Capture page snapshot",
        description="Capture accessibility snapshot of the current page",
        input_schema=EmptyInputSchema,
        tool_type=ToolType.READ_ONLY,
    )

    return Tool(capability=ToolCapability.VISION, schema=schema, handle=handle)


def get_screenshot_tools(capture_snapshot: bool = True) -> list[Tool]:
    """Screenshot tools that match TypeScript screenshot tools"""
    return [
        browser_screenshot_factory(capture_snapshot),
        browser_save_screenshot_factory(capture_snapshot),
    ]


def get_vision_screen_tools(capture_snapshot: bool = True) -> list[Tool]:
    """Vision screen tools that match TypeScript vision tools"""
    return [
        browser_screen_click_factory(capture_snapshot),
        browser_capture_snapshot_factory(capture_snapshot),
    ]


def get_vision_tools(capture_snapshot: bool = True) -> list[Tool]:
    """All vision tools for backward compatibility"""
    return [
        browser_screenshot_factory(capture_snapshot),
        browser_save_screenshot_factory(capture_snapshot),
        browser_screen_click_factory(capture_snapshot),
        browser_capture_snapshot_factory(capture_snapshot),
    ]


VISION_TOOLS = get_vision_tools()
