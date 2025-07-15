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
    ScreenshotInputSchema,
    SaveScreenshotInputSchema,
    ScreenClickInputSchema,
    ScreenDragInputSchema,
    ScreenTypeInputSchema,
    ScreenMoveMouseInputSchema,
    EmptyInputSchema,
)
from services.vision_service import VisionService

if TYPE_CHECKING:
    from context import ServerContext


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

        service = VisionService(context)

        code = [
            f"# Take screenshot of current page",
            f"# Full page: {validated_params.full_page}",
        ]

        async def action() -> ToolActionResult:
            result = await service.take_screenshot(validated_params.full_page)

            if result.success:
                content = [{"type": "text", "text": result.message}]

                # Add screenshot to content if available and client supports images
                if (
                    context.client_supports_images()
                    and result.data
                    and result.data.get("has_screenshot")
                    and result.data.get("content")
                ):
                    import base64

                    screenshot_data = result.data["content"][0]["data"]
                    if screenshot_data:
                        content.append(
                            {
                                "type": "image",
                                "data": base64.b64encode(screenshot_data).decode(),
                                "mimeType": "image/png",
                            }
                        )

                return ToolActionResult(content=content)
            else:
                return ToolActionResult(
                    content=[{"type": "text", "text": result.message}]
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

        service = VisionService(context)

        code = [
            f"# Save screenshot to file",
            f"# Filename: {validated_params.filename}",
            f"# Full page: {validated_params.full_page}",
        ]

        async def action() -> ToolActionResult:
            result = await service.save_screenshot(
                validated_params.filename, validated_params.full_page
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

        service = VisionService(context)

        code = [
            f"# Click at screen coordinates",
            f"# Position: ({validated_params.x}, {validated_params.y})",
            f"# Element: {validated_params.element}",
        ]

        async def action() -> ToolActionResult:
            result = await service.screen_click(
                validated_params.x, validated_params.y, validated_params.element
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
        service = VisionService(context)

        code = [
            "# Capture page snapshot",
            "# Includes accessibility tree and page content",
        ]

        async def action() -> ToolActionResult:
            result = await service.capture_snapshot(include_screenshot=capture_snapshot)

            if result.success:
                return ToolActionResult(
                    content=[{"type": "text", "text": result.data.get("text", "")}]
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
