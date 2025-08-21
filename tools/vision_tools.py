from mcp.server.fastmcp import FastMCP, Context
from context import ServerContext
from services import VisionService
from mcp.types import TextContent, ImageContent, Content
from typing import Optional, Dict


def register_vision_tools(app: FastMCP, server_context: ServerContext) -> None:
    @app.tool()
    async def browser_take_screenshot(
        context: Context,
        full_page: bool = True,
        quality: Optional[int] = 80,
        format: str = "png",
        element_selector: Optional[str] = None,
        clip_region: Optional[Dict[str, int]] = None,
        omit_background: bool = False,
        scale: str = "css",
    ) -> list[Content]:
        service = VisionService(server_context)
        result = await service.take_screenshot(
            full_page=full_page,
            quality=quality,
            format=format,
            element_selector=element_selector,
            clip_region=clip_region,
            omit_background=omit_background,
            scale=scale,
        )

        if result.success:
            content = [TextContent(type="text", text=result.message)]
            if result.data and result.data.get("content"):
                for item in result.data["content"]:
                    if item.get("type") == "screenshot" and item.get("data"):
                        content.append(
                            ImageContent(
                                type="image",
                                data=item["data"],
                                mimeType=f"image/{format}",
                            )
                        )

            return content
        else:
            return [TextContent(type="text", text=f"Screenshot failed: {result.error}")]

    @app.tool()
    async def browser_screen_click(x: int, y: int, context: Context) -> str:
        service = VisionService(server_context)
        result = await service.screen_click(x, y)
        return (
            f"Successfully clicked at ({x}, {y})"
            if result.success
            else f"Screen click failed: {result.error}"
        )

    @app.tool()
    async def browser_screen_drag(
        start_x: int, start_y: int, end_x: int, end_y: int, context: Context
    ) -> str:
        service = VisionService(server_context)
        result = await service.screen_drag(start_x, start_y, end_x, end_y)
        return (
            f"Successfully dragged from ({start_x}, {start_y}) to ({end_x}, {end_y})"
            if result.success
            else f"Screen drag failed: {result.error}"
        )

    @app.tool()
    async def browser_screen_type(x: int, y: int, text: str, context: Context) -> str:
        service = VisionService(server_context)
        result = await service.screen_type(x, y, text)
        return (
            f"Successfully typed '{text}' at ({x}, {y})"
            if result.success
            else f"Screen type failed: {result.error}"
        )

    @app.tool()
    async def browser_screen_move_mouse(x: int, y: int, context: Context) -> str:
        service = VisionService(server_context)
        result = await service.move_mouse(x, y)
        return (
            f"Successfully moved mouse to ({x}, {y})"
            if result.success
            else f"Mouse move failed: {result.error}"
        )
