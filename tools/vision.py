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
    title="Take Enhanced Screenshot",
    description="Take a screenshot with advanced options including quality control, element-specific capture, and region clipping",
    input_schema=ScreenshotInputSchema,
    tool_type=ToolType.READ_ONLY,
)
def browser_screenshot_factory(capture_snapshot: bool) -> Tool:
    async def handle(context: "ServerContext", params: Dict[str, Any]) -> ToolResult:
        validated_params = ScreenshotInputSchema(**params)

        service = VisionService(context)

        code = [
            f"# Take enhanced screenshot with advanced options",
            f"# Full page: {validated_params.full_page}",
            f"# Format: {validated_params.format}",
            f"# Quality: {validated_params.quality}",
        ]

        if validated_params.element_selector:
            code.append(f"# Element: {validated_params.element_selector}")
        if validated_params.clip_region:
            code.append(f"# Clip region: {validated_params.clip_region}")

        async def action() -> ToolActionResult:
            result = await service.take_screenshot(
                full_page=validated_params.full_page,
                quality=validated_params.quality,
                format=validated_params.format,
                element_selector=validated_params.element_selector,
                clip_region=validated_params.clip_region,
                omit_background=validated_params.omit_background,
                scale=validated_params.scale,
            )

            if result.success:
                content = [{"type": "text", "text": result.message}]

                # Add screenshot to content if available and client supports images
                if (
                    context.client_supports_images()
                    and result.data
                    and result.data.get("has_screenshot")
                    and result.data.get("content")
                    and len(result.data["content"]) > 0
                ):
                    import base64

                    screenshot_data = result.data["content"][0]["data"]
                    if screenshot_data and len(screenshot_data) > 0:
                        try:
                            # Safely encode screenshot data
                            if isinstance(screenshot_data, bytes):
                                encoded_data = base64.b64encode(
                                    screenshot_data
                                ).decode()
                            else:
                                # If already string, assume it's base64 encoded
                                encoded_data = screenshot_data

                            content.append(
                                {
                                    "type": "image",
                                    "data": encoded_data,
                                    "mimeType": f"image/{validated_params.format}",
                                }
                            )
                        except Exception as e:
                            content.append(
                                {
                                    "type": "text",
                                    "text": f"Screenshot captured but failed to encode for display: {str(e)}",
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
        title="Take Enhanced Screenshot",
        description="Take a screenshot with advanced options including quality control, element-specific capture, and region clipping",
        input_schema=ScreenshotInputSchema,
        tool_type=ToolType.READ_ONLY,
    )

    return Tool(capability=ToolCapability.VISION, schema=schema, handle=handle)


@define_tool_factory(
    capability=ToolCapability.VISION,
    name="browser_save_screenshot",
    title="Save Enhanced Screenshot",
    description="Save a screenshot to file with comprehensive options and validation",
    input_schema=SaveScreenshotInputSchema,
    tool_type=ToolType.READ_ONLY,
)
def browser_save_screenshot_factory(capture_snapshot: bool) -> Tool:
    async def handle(context: "ServerContext", params: Dict[str, Any]) -> ToolResult:
        validated_params = SaveScreenshotInputSchema(**params)

        service = VisionService(context)

        code = [
            f"# Save enhanced screenshot to file",
            f"# Filename: {validated_params.filename}",
            f"# Full page: {validated_params.full_page}",
            f"# Format: {validated_params.format}",
            f"# Quality: {validated_params.quality}",
        ]

        if validated_params.element_selector:
            code.append(f"# Element: {validated_params.element_selector}")
        if validated_params.clip_region:
            code.append(f"# Clip region: {validated_params.clip_region}")

        async def action() -> ToolActionResult:
            result = await service.save_screenshot(
                filename=validated_params.filename,
                full_page=validated_params.full_page,
                quality=validated_params.quality,
                format=validated_params.format,
                element_selector=validated_params.element_selector,
                clip_region=validated_params.clip_region,
                create_directories=validated_params.create_directories,
                overwrite=validated_params.overwrite,
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
        title="Save Enhanced Screenshot",
        description="Save a screenshot to file with comprehensive options and validation",
        input_schema=SaveScreenshotInputSchema,
        tool_type=ToolType.READ_ONLY,
    )

    return Tool(capability=ToolCapability.VISION, schema=schema, handle=handle)


@define_tool_factory(
    capability=ToolCapability.VISION,
    name="browser_screen_click",
    title="Advanced Screen Click",
    description="Click at screen coordinates with comprehensive validation and advanced options",
    input_schema=ScreenClickInputSchema,
    tool_type=ToolType.DESTRUCTIVE,
)
def browser_screen_click_factory(capture_snapshot: bool) -> Tool:
    async def handle(context: "ServerContext", params: Dict[str, Any]) -> ToolResult:
        validated_params = ScreenClickInputSchema(**params)

        service = VisionService(context)

        code = [
            f"# Advanced screen click with validation",
            f"# Position: ({validated_params.x}, {validated_params.y})",
            f"# Element: {validated_params.element}",
            f"# Click type: {validated_params.click_type}",
            f"# Modifiers: {validated_params.modifiers}",
            f"# Validate bounds: {validated_params.validate_bounds}",
        ]

        async def action() -> ToolActionResult:
            result = await service.screen_click(
                x=validated_params.x,
                y=validated_params.y,
                element=validated_params.element,
                click_type=validated_params.click_type,
                modifiers=validated_params.modifiers,
                button_delay=validated_params.button_delay,
                click_count=validated_params.click_count,
                force=validated_params.force,
                validate_bounds=validated_params.validate_bounds,
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
        title="Advanced Screen Click",
        description="Click at screen coordinates with comprehensive validation and advanced options",
        input_schema=ScreenClickInputSchema,
        tool_type=ToolType.DESTRUCTIVE,
    )

    return Tool(capability=ToolCapability.VISION, schema=schema, handle=handle)


@define_tool_factory(
    capability=ToolCapability.VISION,
    name="browser_screen_drag",
    title="Advanced Screen Drag",
    description="Drag between screen coordinates with smooth movement and validation",
    input_schema=ScreenDragInputSchema,
    tool_type=ToolType.DESTRUCTIVE,
)
def browser_screen_drag_factory(capture_snapshot: bool) -> Tool:
    async def handle(context: "ServerContext", params: Dict[str, Any]) -> ToolResult:
        validated_params = ScreenDragInputSchema(**params)

        service = VisionService(context)

        code = [
            f"# Advanced screen drag with smooth movement",
            f"# From: ({validated_params.from_x}, {validated_params.from_y})",
            f"# To: ({validated_params.to_x}, {validated_params.to_y})",
            f"# Element: {validated_params.element}",
            f"# Modifiers: {validated_params.modifiers}",
            f"# Steps: {validated_params.steps}",
        ]

        async def action() -> ToolActionResult:
            result = await service.screen_drag(
                from_x=validated_params.from_x,
                from_y=validated_params.from_y,
                to_x=validated_params.to_x,
                to_y=validated_params.to_y,
                element=validated_params.element,
                modifiers=validated_params.modifiers,
                steps=validated_params.steps,
                validate_bounds=validated_params.validate_bounds,
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
        name="browser_screen_drag",
        title="Advanced Screen Drag",
        description="Drag between screen coordinates with smooth movement and validation",
        input_schema=ScreenDragInputSchema,
        tool_type=ToolType.DESTRUCTIVE,
    )

    return Tool(capability=ToolCapability.VISION, schema=schema, handle=handle)


@define_tool_factory(
    capability=ToolCapability.VISION,
    name="browser_screen_type",
    title="Type at Screen Coordinates",
    description="Type text at specific screen coordinates with validation and options",
    input_schema=ScreenTypeInputSchema,
    tool_type=ToolType.DESTRUCTIVE,
)
def browser_screen_type_factory(capture_snapshot: bool) -> Tool:
    async def handle(context: "ServerContext", params: Dict[str, Any]) -> ToolResult:
        validated_params = ScreenTypeInputSchema(**params)

        service = VisionService(context)

        code = [
            f"# Type text at screen coordinates",
            f"# Position: ({validated_params.x}, {validated_params.y})",
            f"# Element: {validated_params.element}",
            f"# Text length: {len(validated_params.text)}",
            f"# Delay: {validated_params.delay}ms",
            f"# Clear first: {validated_params.clear_first}",
        ]

        async def action() -> ToolActionResult:
            result = await service.screen_type(
                x=validated_params.x,
                y=validated_params.y,
                text=validated_params.text,
                element=validated_params.element,
                delay=validated_params.delay,
                clear_first=validated_params.clear_first,
                validate_bounds=validated_params.validate_bounds,
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
        name="browser_screen_type",
        title="Type at Screen Coordinates",
        description="Type text at specific screen coordinates with validation and options",
        input_schema=ScreenTypeInputSchema,
        tool_type=ToolType.DESTRUCTIVE,
    )

    return Tool(capability=ToolCapability.VISION, schema=schema, handle=handle)


@define_tool_factory(
    capability=ToolCapability.VISION,
    name="browser_move_mouse",
    title="Move Mouse to Coordinates",
    description="Move mouse to specific screen coordinates with smooth movement",
    input_schema=ScreenMoveMouseInputSchema,
    tool_type=ToolType.DESTRUCTIVE,
)
def browser_move_mouse_factory(capture_snapshot: bool) -> Tool:
    async def handle(context: "ServerContext", params: Dict[str, Any]) -> ToolResult:
        validated_params = ScreenMoveMouseInputSchema(**params)

        service = VisionService(context)

        code = [
            f"# Move mouse to coordinates with smooth movement",
            f"# Position: ({validated_params.x}, {validated_params.y})",
            f"# Element: {validated_params.element}",
            f"# Steps: {validated_params.steps}",
        ]

        async def action() -> ToolActionResult:
            result = await service.move_mouse(
                x=validated_params.x,
                y=validated_params.y,
                element=validated_params.element,
                steps=validated_params.steps,
                validate_bounds=validated_params.validate_bounds,
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
        name="browser_move_mouse",
        title="Move Mouse to Coordinates",
        description="Move mouse to specific screen coordinates with smooth movement",
        input_schema=ScreenMoveMouseInputSchema,
        tool_type=ToolType.DESTRUCTIVE,
    )

    return Tool(capability=ToolCapability.VISION, schema=schema, handle=handle)


@define_tool_factory(
    capability=ToolCapability.VISION,
    name="browser_capture_snapshot",
    title="Capture Enhanced Page Snapshot",
    description="Capture accessibility snapshot of the current page with enhanced error handling",
    input_schema=EmptyInputSchema,
    tool_type=ToolType.READ_ONLY,
)
def browser_capture_snapshot_factory(capture_snapshot: bool) -> Tool:
    async def handle(context: "ServerContext", params: Dict[str, Any]) -> ToolResult:
        service = VisionService(context)

        code = [
            "# Capture enhanced page snapshot",
            "# Includes accessibility tree, page content, and element references",
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
        title="Capture Enhanced Page Snapshot",
        description="Capture accessibility snapshot of the current page with enhanced error handling",
        input_schema=EmptyInputSchema,
        tool_type=ToolType.READ_ONLY,
    )

    return Tool(capability=ToolCapability.VISION, schema=schema, handle=handle)


def get_screenshot_tools(capture_snapshot: bool = True) -> list[Tool]:
    """Enhanced screenshot tools with advanced functionality"""
    return [
        browser_screenshot_factory(capture_snapshot),
        browser_save_screenshot_factory(capture_snapshot),
    ]


def get_vision_screen_tools(capture_snapshot: bool = True) -> list[Tool]:
    """Enhanced vision screen tools with comprehensive validation"""
    return [
        browser_screen_click_factory(capture_snapshot),
        browser_screen_drag_factory(capture_snapshot),
        browser_screen_type_factory(capture_snapshot),
        browser_move_mouse_factory(capture_snapshot),
        browser_capture_snapshot_factory(capture_snapshot),
    ]


def get_vision_tools(capture_snapshot: bool = True) -> list[Tool]:
    """All enhanced vision tools for enterprise-grade automation"""
    return [
        browser_screenshot_factory(capture_snapshot),
        browser_save_screenshot_factory(capture_snapshot),
        browser_screen_click_factory(capture_snapshot),
        browser_screen_drag_factory(capture_snapshot),
        browser_screen_type_factory(capture_snapshot),
        browser_move_mouse_factory(capture_snapshot),
        browser_capture_snapshot_factory(capture_snapshot),
    ]


VISION_TOOLS = get_vision_tools()
