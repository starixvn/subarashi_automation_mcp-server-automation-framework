from typing import Dict, Any, TYPE_CHECKING
from .tool_schema import (
    define_tool,
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
    ClickInputSchema,
    TypeInputSchema,
    HoverInputSchema,
    SelectOptionInputSchema,
    GetTextInputSchema,
    WaitForSelectorInputSchema,
    DragInputSchema,
)

if TYPE_CHECKING:
    from ..context import ServerContext



async def generate_locator_string(locator) -> str:
    try:
        if hasattr(locator, "_generate_locator_string"):
            return await locator._generate_locator_string()
        elif hasattr(locator, "locator"):
            return str(locator)
        else:
            return f"locator('{locator}')"
    except Exception:
        return f"locator('{locator}')"


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

        tab = context.current_tab_or_die()
        snapshot = tab.snapshot_or_die()

        locator = snapshot.ref_locator(
            {"element": validated_params.element, "ref": validated_params.ref}
        )

        locator_string = await generate_locator_string(locator)

        code = [
            f"// Click {validated_params.element}",
            f"await page.{locator_string}.click();",
        ]

        async def action() -> ToolActionResult:
            try:
                await locator.click()
                return ToolActionResult(content=[])
            except Exception as e:
                return ToolActionResult(
                    content=[
                        {
                            "type": "text",
                            "text": f"Failed to click {validated_params.element}: {str(e)}",
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

        tab = context.current_tab_or_die()
        snapshot = tab.snapshot_or_die()

        locator = snapshot.ref_locator(
            {"element": validated_params.element, "ref": validated_params.ref}
        )

        locator_string = await generate_locator_string(locator)

        code = []
        steps = []

        if validated_params.slowly:
            code.append(
                f'// Press "{validated_params.text}" sequentially into "{validated_params.element}"'
            )
            code.append(
                f"await page.{locator_string}.pressSequentially('{validated_params.text}');"
            )
            steps.append(lambda: locator.press_sequentially(validated_params.text))
        else:
            code.append(
                f'// Fill "{validated_params.text}" into "{validated_params.element}"'
            )
            code.append(f"await page.{locator_string}.fill('{validated_params.text}');")
            steps.append(lambda: locator.fill(validated_params.text))

        if validated_params.submit:
            code.append("// Submit text")
            code.append(f"await page.{locator_string}.press('Enter');")
            steps.append(lambda: locator.press("Enter"))

        async def action() -> ToolActionResult:
            try:
                for step in steps:
                    await step()
                return ToolActionResult(content=[])
            except Exception as e:
                return ToolActionResult(
                    content=[
                        {
                            "type": "text",
                            "text": f"Failed to type into {validated_params.element}: {str(e)}",
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

        tab = context.current_tab_or_die()
        snapshot = tab.snapshot_or_die()

        locator = snapshot.ref_locator(
            {"element": validated_params.element, "ref": validated_params.ref}
        )

        locator_string = await generate_locator_string(locator)

        code = [
            f"// Hover over {validated_params.element}",
            f"await page.{locator_string}.hover();",
        ]

        async def action() -> ToolActionResult:
            try:
                await locator.hover()
                return ToolActionResult(
                    content=[
                        {
                            "type": "text",
                            "text": f"Hovered over {validated_params.element}",
                        }
                    ]
                )
            except Exception as e:
                return ToolActionResult(
                    content=[
                        {
                            "type": "text",
                            "text": f"Failed to hover over {validated_params.element}: {str(e)}",
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

        tab = context.current_tab_or_die()
        snapshot = tab.snapshot_or_die()

        locator = snapshot.ref_locator(
            {"element": validated_params.element, "ref": validated_params.ref}
        )

        locator_string = await generate_locator_string(locator)

        code = [
            f"// Select options {validated_params.values} in {validated_params.element}",
            f"await page.{locator_string}.selectOption({validated_params.values});",
        ]

        async def action() -> ToolActionResult:
            try:
                await locator.select_option(validated_params.values)
                return ToolActionResult(
                    content=[
                        {
                            "type": "text",
                            "text": f"Selected {validated_params.values} in {validated_params.element}",
                        }
                    ]
                )
            except Exception as e:
                return ToolActionResult(
                    content=[
                        {
                            "type": "text",
                            "text": f"Failed to select option in {validated_params.element}: {str(e)}",
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

        tab = context.current_tab_or_die()

        code = [
            f"// Get text from '{validated_params.selector}'",
            f"const text = await page.textContent('{validated_params.selector}');",
        ]

        async def action() -> ToolActionResult:
            try:
                text = await tab.page.text_content(validated_params.selector)
                return ToolActionResult(
                    content=[
                        {
                            "type": "text",
                            "text": f"Text content: {text or '(empty)'}",
                        }
                    ]
                )
            except Exception as e:
                return ToolActionResult(
                    content=[
                        {
                            "type": "text",
                            "text": f"Failed to get text from {validated_params.selector}: {str(e)}",
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
    name="browser_drag",
    title="Drag element",
    description="Drag element from source to target",
    input_schema=DragInputSchema,
    tool_type=ToolType.DESTRUCTIVE,
)
def browser_drag_factory(capture_snapshot: bool) -> Tool:
    async def handle(context: "ServerContext", params: Dict[str, Any]) -> ToolResult:
        validated_params = DragInputSchema(**params)

        tab = context.current_tab_or_die()
        snapshot = tab.snapshot_or_die()

        start_locator = snapshot.ref_locator(
            {"element": validated_params.start_element, "ref": validated_params.start_ref}
        )
        end_locator = snapshot.ref_locator(
            {"element": validated_params.end_element, "ref": validated_params.end_ref}
        )

        start_locator_string = await generate_locator_string(start_locator)
        end_locator_string = await generate_locator_string(end_locator)

        code = [
            f"// Drag from {validated_params.start_element} to {validated_params.end_element}",
            f"await page.{start_locator_string}.dragTo(page.{end_locator_string});",
        ]

        async def action() -> ToolActionResult:
            try:
                await start_locator.drag_to(end_locator)
                return ToolActionResult(
                    content=[
                        {
                            "type": "text",
                            "text": f"Dragged from {validated_params.start_element} to {validated_params.end_element}",
                        }
                    ]
                )
            except Exception as e:
                return ToolActionResult(
                    content=[
                        {
                            "type": "text",
                            "text": f"Failed to drag: {str(e)}",
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
        browser_drag_factory(capture_snapshot),
    ]


INTERACTION_TOOLS = get_interaction_tools()