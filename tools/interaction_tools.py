from mcp.server.fastmcp import FastMCP, Context
from context import ServerContext
from services import InteractionService, CoreService
from mcp.types import TextContent, Content
from typing import Optional, List


def register_interaction_tools(app: FastMCP, server_context: ServerContext) -> None:
    @app.tool()
    async def browser_click(
        context: Context,
        element: str,
        ref: str,
        modifiers: Optional[List[str]] = None,
        button: str = "left",
        click_count: int = 1,
        delay: int = 0,
    ) -> list[Content]:
        service = InteractionService(server_context)
        element_ref = {"ref": ref, "element": element}

        result = await service.click_element(
            element_ref,
            modifiers=modifiers or [],
            click_type=button,
            click_count=click_count,
            button_delay=delay,
        )

        if result.success:
            core_service = CoreService(server_context)
            url_result = await core_service.get_current_url()
            title_result = await core_service.get_page_title()

            current_url = (
                url_result["data"]["url"] if url_result["success"] else "Unknown"
            )
            page_title = (
                title_result["data"]["title"] if title_result["success"] else "Unknown"
            )

            message = "**Click Completed Successfully**\n\n"
            message += f"**Element:** {element} (ref: {ref})\n"
            message += f"**Button:** {button}\n"
            message += f"**Count:** {click_count}\n"
            if modifiers:
                message += f"**Modifiers:** {', '.join(modifiers)}\n"
            message += f"\n**Current URL:** {current_url}\n"
            message += f"**Page Title:** {page_title}\n"
            message += "**Status:** Click action completed and page updated"

            return [TextContent(type="text", text=message)]
        else:
            return [TextContent(type="text", text=f"**Click Failed:** {result.error}")]

    @app.tool()
    async def browser_type(
        context: Context,
        element: str,
        ref: str,
        text: str,
        slowly: bool = False,
        submit: bool = False,
        clear_first: bool = True,
    ) -> list[Content]:
        service = InteractionService(server_context)
        element_ref = {"ref": ref, "element": element}

        result = await service.type_text(
            element_ref, text, slowly=slowly, submit=submit, clear_first=clear_first
        )

        if result.success:
            core_service = CoreService(server_context)
            url_result = await core_service.get_current_url()
            title_result = await core_service.get_page_title()

            current_url = (
                url_result["data"]["url"] if url_result["success"] else "Unknown"
            )
            page_title = (
                title_result["data"]["title"] if title_result["success"] else "Unknown"
            )

            message = "**Text Input Completed Successfully**\n\n"
            message += f"**Element:** {element} (ref: {ref})\n"
            message += f"**Text:** '{text}'\n"
            message += f"**Typing Mode:** {'Slow (character by character)' if slowly else 'Fast (fill)'}\n"
            message += f"**Submit:** {'Yes (pressed Enter)' if submit else 'No'}\n"
            message += f"**Clear First:** {'Yes' if clear_first else 'No'}\n"
            message += f"\n**Current URL:** {current_url}\n"
            message += f"**Page Title:** {page_title}\n"
            message += "**Status:** Text input completed and page updated"

            return [TextContent(type="text", text=message)]
        else:
            return [TextContent(type="text", text=f"**Type Failed:** {result.error}")]

    @app.tool()
    async def browser_hover(
        context: Context, element: str, ref: str, duration: int = 1000
    ) -> list[Content]:
        service = InteractionService(server_context)
        element_ref = {"ref": ref, "element": element}

        result = await service.hover_element(element_ref)

        if result.success:
            message = "**Hover Completed Successfully**\n\n"
            message += f"**Element:** {element} (ref: {ref})\n"
            message += f"**Duration:** {duration}ms\n"
            message += (
                "**Status:** Hover action completed, element should show hover state"
            )

            return [TextContent(type="text", text=message)]
        else:
            return [TextContent(type="text", text=f"**Hover Failed:** {result.error}")]

    @app.tool()
    async def browser_select_option(
        context: Context,
        element: str,
        ref: str,
        value: Optional[str] = None,
        label: Optional[str] = None,
        index: Optional[int] = None,
    ) -> list[Content]:
        service = InteractionService(server_context)
        element_ref = {"ref": ref, "element": element}

        if value:
            values = [value]
        elif label:
            values = [label]  # Service should handle label-based selection
        elif index is not None:
            values = [str(index)]  # Service should handle index-based selection
        else:
            return [
                TextContent(
                    type="text",
                    text="**Select Failed:** Must provide either value, label, or index",
                )
            ]

        result = await service.select_option(element_ref, values)

        if result.success:
            selection_method = (
                f"value '{value}'"
                if value
                else f"label '{label}'"
                if label
                else f"index {index}"
            )

            message = "**Option Selected Successfully**\n\n"
            message += f"**Element:** {element} (ref: {ref})\n"
            message += f"**Selection:** {selection_method}\n"
            message += "**Status:** Option selection completed"

            return [TextContent(type="text", text=message)]
        else:
            return [TextContent(type="text", text=f"**Select Failed:** {result.error}")]

    @app.tool()
    async def browser_get_text(
        context: Context, element: str, ref: str
    ) -> list[Content]:
        service = InteractionService(server_context)
        element_ref = {"ref": ref, "element": element}
        result = await service.get_text_content(element_ref=element_ref)

        if result.success:
            text_content = result.data.get("text", "")

            message = "**Text Content Retrieved Successfully**\n\n"
            message += f"**Element:** {element} (ref: {ref})\n"
            message += f"**Text Length:** {len(text_content)} characters\n\n"
            message += f"**Content:**\n```\n{text_content}\n```"

            return [TextContent(type="text", text=message)]
        else:
            return [
                TextContent(type="text", text=f"**Get Text Failed:** {result.error}")
            ]

    @app.tool()
    async def browser_drag(
        context: Context,
        start_element: str,
        start_ref: str,
        end_element: str,
        end_ref: str,
    ) -> list[Content]:
        service = InteractionService(server_context)
        start_ref_dict = {"ref": start_ref, "element": start_element}
        end_ref_dict = {"ref": end_ref, "element": end_element}

        result = await service.drag_element(start_ref_dict, end_ref_dict)

        if result.success:
            message = "**Drag Operation Completed Successfully**\n\n"
            message += f"**From Element:** {start_element} (ref: {start_ref})\n"
            message += f"**To Element:** {end_element} (ref: {end_ref})\n"
            message += "**Status:** Drag and drop action completed"

            return [TextContent(type="text", text=message)]
        else:
            return [TextContent(type="text", text=f"**Drag Failed:** {result.error}")]
