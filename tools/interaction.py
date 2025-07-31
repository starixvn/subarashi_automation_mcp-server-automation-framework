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
    ClickInputSchema,
    TypeInputSchema,
    HoverInputSchema,
    SelectOptionInputSchema,
    GetTextInputSchema,
    GetContentsInputSchema,
    DragInputSchema,
)
from services.interaction_service import InteractionService

if TYPE_CHECKING:
    from ..context import ServerContext


@define_tool_factory(
    capability=ToolCapability.CORE,
    name="browser_click",
    title="Click",
    description="Perform click on a web page",
    input_schema=ClickInputSchema,
    tool_type=ToolType.DESTRUCTIVE,
)
def browser_click_factory(capture_snapshot: bool) -> Tool:
    async def handle(context: "ServerContext", params: Dict[str, Any]) -> ToolResult:
        validated_params = ClickInputSchema(**params)

        service = InteractionService(context)

        element_ref = {"element": validated_params.element, "ref": validated_params.ref}

        code = [
            f"# Click on {validated_params.element}",
            f"# Using element reference: {validated_params.ref}",
        ]

        async def action() -> ToolActionResult:
            result = await service.click_element(element_ref)

            if result.success:
                return ToolActionResult(content=[])
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
            wait_for_network=True,
        )

    schema = ToolSchema(
        name="browser_click",
        title="Click",
        description="Perform click on a web page",
        input_schema=ClickInputSchema,
        tool_type=ToolType.DESTRUCTIVE,
    )

    return Tool(capability=ToolCapability.CORE, schema=schema, handle=handle)


@define_tool_factory(
    capability=ToolCapability.CORE,
    name="browser_type",
    title="Type text",
    description="Type text into editable element",
    input_schema=TypeInputSchema,
    tool_type=ToolType.DESTRUCTIVE,
)
def browser_type_factory(capture_snapshot: bool) -> Tool:
    async def handle(context: "ServerContext", params: Dict[str, Any]) -> ToolResult:
        validated_params = TypeInputSchema(**params)

        service = InteractionService(context)

        element_ref = {"element": validated_params.element, "ref": validated_params.ref}

        code = [
            f"# Type text into {validated_params.element}",
            f"# Text: '{validated_params.text}'",
        ]

        if validated_params.slowly:
            code.append("# Using slow typing (press sequentially)")

        if validated_params.submit:
            code.append("# Submit after typing (press Enter)")

        async def action() -> ToolActionResult:
            result = await service.type_text(
                element_ref,
                validated_params.text,
                slowly=validated_params.slowly,
                submit=validated_params.submit,
            )

            if result.success:
                return ToolActionResult(content=[])
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
            wait_for_network=True,
        )

    schema = ToolSchema(
        name="browser_type",
        title="Type text",
        description="Type text into editable element",
        input_schema=TypeInputSchema,
        tool_type=ToolType.DESTRUCTIVE,
    )

    return Tool(capability=ToolCapability.CORE, schema=schema, handle=handle)


@define_tool_factory(
    capability=ToolCapability.CORE,
    name="browser_hover",
    title="Hover mouse",
    description="Hover over element on page",
    input_schema=HoverInputSchema,
    tool_type=ToolType.READ_ONLY,
)
def browser_hover_factory(capture_snapshot: bool) -> Tool:
    async def handle(context: "ServerContext", params: Dict[str, Any]) -> ToolResult:
        validated_params = HoverInputSchema(**params)

        service = InteractionService(context)

        element_ref = {"element": validated_params.element, "ref": validated_params.ref}

        code = [
            f"# Hover over {validated_params.element}",
            f"# Using element reference: {validated_params.ref}",
        ]

        async def action() -> ToolActionResult:
            result = await service.hover_element(element_ref)

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
        name="browser_hover",
        title="Hover mouse",
        description="Hover over element on page",
        input_schema=HoverInputSchema,
        tool_type=ToolType.READ_ONLY,
    )

    return Tool(capability=ToolCapability.CORE, schema=schema, handle=handle)


@define_tool_factory(
    capability=ToolCapability.CORE,
    name="browser_select_option",
    title="Select option",
    description="Select an option in a dropdown",
    input_schema=SelectOptionInputSchema,
    tool_type=ToolType.DESTRUCTIVE,
)
def browser_select_option_factory(capture_snapshot: bool) -> Tool:
    async def handle(context: "ServerContext", params: Dict[str, Any]) -> ToolResult:
        validated_params = SelectOptionInputSchema(**params)

        service = InteractionService(context)

        element_ref = {"element": validated_params.element, "ref": validated_params.ref}

        code = [
            f"# Select options in {validated_params.element}",
            f"# Values: {validated_params.values}",
        ]

        async def action() -> ToolActionResult:
            result = await service.select_option(element_ref, validated_params.values)

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
        name="browser_select_option",
        title="Select option",
        description="Select an option in a dropdown",
        input_schema=SelectOptionInputSchema,
        tool_type=ToolType.DESTRUCTIVE,
    )

    return Tool(capability=ToolCapability.CORE, schema=schema, handle=handle)


@define_tool_factory(
    capability=ToolCapability.CORE,
    name="browser_get_text",
    title="Get text",
    description="Get text content from element",
    input_schema=GetTextInputSchema,
    tool_type=ToolType.READ_ONLY,
)
def browser_get_text_factory(capture_snapshot: bool) -> Tool:
    async def handle(context: "ServerContext", params: Dict[str, Any]) -> ToolResult:
        validated_params = GetTextInputSchema(**params)

        service = InteractionService(context)

        code = [
            f"# Get text content from element",
            f"# Selector: '{validated_params.selector}'",
        ]

        async def action() -> ToolActionResult:
            result = await service.get_text_content(validated_params.selector)

            if result.success:
                return ToolActionResult(
                    content=[
                        {
                            "type": "text",
                            "text": f"Text content: {result.data['text']}",
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
        name="browser_get_text",
        title="Get text",
        description="Get text content from element",
        input_schema=GetTextInputSchema,
        tool_type=ToolType.READ_ONLY,
    )

    return Tool(capability=ToolCapability.CORE, schema=schema, handle=handle)


@define_tool_factory(
    capability=ToolCapability.CORE,
    name="browser_get_contents",
    title="Get Enhanced Contents",
    description="Get enhanced text content with optional screenshot from web page element. Optimized for n8n integration.",
    input_schema=GetContentsInputSchema,
    tool_type=ToolType.READ_ONLY,
)
def browser_get_contents_factory(capture_snapshot: bool) -> Tool:
    async def handle(context: "ServerContext", params: Dict[str, Any]) -> ToolResult:
        validated_params = GetContentsInputSchema(**params)

        service = InteractionService(context)

        if hasattr(validated_params, "selector") and validated_params.selector:
            target_description = f"CSS selector: {validated_params.selector}"
        elif hasattr(validated_params, "element_ref") and validated_params.element_ref:
            if hasattr(validated_params.element_ref, "element"):
                element_desc = validated_params.element_ref.element
            else:
                element_desc = validated_params.element_ref.get("element", "Unknown")
            target_description = f"Element: {element_desc}"
        else:
            target_description = "Unknown target"

        code = [
            f"# Get enhanced contents from: {target_description}",
            f"# Preserve formatting: {validated_params.preserve_formatting}",
            f"# Include screenshot: {validated_params.include_screenshot}",
        ]

        async def action() -> ToolActionResult:
            try:
                result = await service.get_contents(
                    selector=getattr(validated_params, "selector", None),
                    element_ref=getattr(validated_params, "element_ref", None),
                    preserve_formatting=validated_params.preserve_formatting,
                    normalize_whitespace=validated_params.normalize_whitespace,
                    include_screenshot=validated_params.include_screenshot,
                    screenshot_quality=validated_params.screenshot_quality,
                )

                if result.success:
                    content = [
                        {
                            "type": "text",
                            "text": f"Successfully extracted content from {target_description}",
                        }
                    ]

                    if result.data and "text" in result.data:
                        content.append(
                            {
                                "type": "text",
                                "text": f"Content: {result.data['text']}",
                            }
                        )

                    if result.data and "screenshot" in result.data:
                        content.append(
                            {
                                "type": "image",
                                "data": result.data["screenshot"],
                                "mimeType": "image/png",
                            }
                        )

                    return ToolActionResult(content=content)
                else:
                    return ToolActionResult(
                        content=[
                            {
                                "type": "text",
                                "text": f"Failed to get contents: {result.error or result.message}",
                            }
                        ]
                    )

            except Exception as e:
                return ToolActionResult(
                    content=[
                        {"type": "text", "text": f"Tool execution error: {str(e)}"}
                    ]
                )

        return ToolResult(
            code=code,
            action=action,
            capture_snapshot=capture_snapshot,
            wait_for_network=False,
        )

    schema = ToolSchema(
        name="browser_get_contents",
        title="Get Enhanced Contents",
        description="Get enhanced text content with optional screenshot from web page element. Optimized for n8n integration.",
        input_schema=GetContentsInputSchema,
        tool_type=ToolType.READ_ONLY,
    )

    return Tool(capability=ToolCapability.CORE, schema=schema, handle=handle)


@define_tool_factory(
    capability=ToolCapability.CORE,
    name="browser_drag",
    title="Drag element",
    description="Drag element from source to target",
    input_schema=DragInputSchema,
    tool_type=ToolType.DESTRUCTIVE,
)
def browser_drag_factory(capture_snapshot: bool) -> Tool:
    async def handle(context: "ServerContext", params: Dict[str, Any]) -> ToolResult:
        validated_params = DragInputSchema(**params)

        service = InteractionService(context)

        start_ref = {
            "element": validated_params.start_element,
            "ref": validated_params.start_ref,
        }
        end_ref = {
            "element": validated_params.end_element,
            "ref": validated_params.end_ref,
        }

        code = [
            f"# Drag element from {validated_params.start_element} to {validated_params.end_element}",
            f"# Start ref: {validated_params.start_ref}",
            f"# End ref: {validated_params.end_ref}",
        ]

        async def action() -> ToolActionResult:
            result = await service.drag_element(start_ref, end_ref)

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
        name="browser_drag",
        title="Drag element",
        description="Drag element from source to target",
        input_schema=DragInputSchema,
        tool_type=ToolType.DESTRUCTIVE,
    )

    return Tool(capability=ToolCapability.CORE, schema=schema, handle=handle)


def get_interaction_tools(capture_snapshot: bool = True) -> list[Tool]:
    return [
        browser_click_factory(capture_snapshot),
        browser_type_factory(capture_snapshot),
        browser_hover_factory(capture_snapshot),
        browser_select_option_factory(capture_snapshot),
        browser_get_text_factory(capture_snapshot),
        browser_get_contents_factory(capture_snapshot),
        browser_drag_factory(capture_snapshot),
    ]


INTERACTION_TOOLS = get_interaction_tools()
