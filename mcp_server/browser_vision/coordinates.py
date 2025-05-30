import logging
import asyncio
from typing import List
from mcp import types
from mcp_server.core.mcp_setup import mcp, get_service_context

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@mcp.tool(
    name="browser_screen_click",
    description="Click at specific screen coordinates."
)
async def browser_screen_click(
    x: int,
    y: int,
    button: str = "left",
    click_count: int = 1
) -> List[types.TextContent]:
    """
    Click at specific screen coordinates.
    
    Args:
        x: X coordinate in pixels
        y: Y coordinate in pixels  
        button: Mouse button ('left', 'right', 'middle')
        click_count: Number of clicks (1 for single, 2 for double)
        
    Returns:
        List of TextContent with click result
    """
    try:
        if not isinstance(x, int) or not isinstance(y, int):
            return [types.TextContent(
                type="text",
                text="Error: X and Y coordinates must be integers"
            )]
        
        if x < 0 or y < 0:
            return [types.TextContent(
                type="text",
                text="Error: Coordinates must be non-negative"
            )]
        
        if button not in ["left", "right", "middle"]:
            return [types.TextContent(
                type="text",
                text="Error: Button must be 'left', 'right', or 'middle'"
            )]
        
        if click_count < 1 or click_count > 3:
            return [types.TextContent(
                type="text",
                text="Error: Click count must be between 1 and 3"
            )]
        
        context = await get_service_context()
        page = await context.playwright_manager.ensure_browser()
        logger.info(f"Clicking at coordinates ({x}, {y}) with {button} button, {click_count} times")
        
        await page.mouse.move(x, y)
        await page.mouse.click(x, y, button=button, click_count=click_count)
        
        click_type = "single click" if click_count == 1 else f"{click_count} clicks"
        
        return [types.TextContent(
            type="text",
            text=f"Successfully performed {click_type} with {button} mouse button at coordinates ({x}, {y})"
        )]
        
    except Exception as e:
        error_msg = f"Failed to click at coordinates: {str(e)}"
        logger.error(error_msg)
        return [types.TextContent(
            type="text",
            text=error_msg
        )]


@mcp.tool(
    name="browser_screen_drag",
    description="Drag from one coordinate to another."
)
async def browser_screen_drag(
    start_x: int,
    start_y: int,
    end_x: int,
    end_y: int,
    steps: int = 10
) -> List[types.TextContent]:
    """
    Drag from start coordinates to end coordinates.
    
    Args:
        start_x: Starting X coordinate
        start_y: Starting Y coordinate
        end_x: Ending X coordinate
        end_y: Ending Y coordinate
        steps: Number of intermediate steps (more steps = smoother drag)
        
    Returns:
        List of TextContent with drag result
    """
    try:
        coords = [start_x, start_y, end_x, end_y]
        if not all(isinstance(coord, int) for coord in coords):
            return [types.TextContent(
                type="text",
                text="Error: All coordinates must be integers"
            )]
        
        if any(coord < 0 for coord in coords):
            return [types.TextContent(
                type="text",
                text="Error: All coordinates must be non-negative"
            )]
        
        if steps < 1 or steps > 100:
            return [types.TextContent(
                type="text",
                text="Error: Steps must be between 1 and 100"
            )]
        
        context = await get_service_context()
        page = await context.playwright_manager.ensure_browser()
        logger.info(f"Dragging from ({start_x}, {start_y}) to ({end_x}, {end_y}) in {steps} steps")
        
        await page.mouse.move(start_x, start_y)
        await page.mouse.down()
        
        for i in range(1, steps + 1):
            progress = i / steps
            current_x = start_x + (end_x - start_x) * progress
            current_y = start_y + (end_y - start_y) * progress
            await page.mouse.move(current_x, current_y)
            await asyncio.sleep(0.01)
        
        await page.mouse.up()
        
        distance = ((end_x - start_x) ** 2 + (end_y - start_y) ** 2) ** 0.5
        
        return [types.TextContent(
            type="text",
            text=f"Successfully dragged from ({start_x}, {start_y}) to ({end_x}, {end_y}) - distance: {distance:.1f} pixels"
        )]
        
    except Exception as e:
        error_msg = f"Failed to perform drag operation: {str(e)}"
        logger.error(error_msg)
        return [types.TextContent(
            type="text",
            text=error_msg
        )]


@mcp.tool(
    name="browser_screen_move_mouse",
    description="Move mouse cursor to specific coordinates without clicking."
)
async def browser_screen_move_mouse(
    x: int,
    y: int,
    smooth: bool = True
) -> List[types.TextContent]:
    """
    Move mouse to specific coordinates.
    
    Args:
        x: X coordinate in pixels
        y: Y coordinate in pixels
        smooth: Whether to move smoothly (with animation)
        
    Returns:
        List of TextContent with move result
    """
    try:
        if not isinstance(x, int) or not isinstance(y, int):
            return [types.TextContent(
                type="text",
                text="Error: X and Y coordinates must be integers"
            )]
        
        if x < 0 or y < 0:
            return [types.TextContent(
                type="text",
                text="Error: Coordinates must be non-negative"
            )]
        
        context = await get_service_context()
        page = await context.playwright_manager.ensure_browser()
        logger.info(f"Moving mouse to coordinates ({x}, {y})")
        
        if smooth:
            current_pos = await page.evaluate("""
                () => {
                    return { x: 0, y: 0 }; // Default position
                }
            """)
            
            steps = 20
            start_x, start_y = current_pos.get("x", 0), current_pos.get("y", 0)
            
            for i in range(1, steps + 1):
                progress = i / steps
                current_x = start_x + (x - start_x) * progress
                current_y = start_y + (y - start_y) * progress
                await page.mouse.move(current_x, current_y)
                await asyncio.sleep(0.005)  # Small delay for smooth movement
        else:
            await page.mouse.move(x, y)
        
        movement_type = "smoothly" if smooth else "directly"
        
        return [types.TextContent(
            type="text",
            text=f"Successfully moved mouse {movement_type} to coordinates ({x}, {y})"
        )]
        
    except Exception as e:
        error_msg = f"Failed to move mouse: {str(e)}"
        logger.error(error_msg)
        return [types.TextContent(
            type="text",
            text=error_msg
        )] 