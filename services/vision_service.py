import asyncio
import logging
from typing import Dict, Any, Optional, List
import hashlib

from .base_service import BaseService, ServiceResult

logger = logging.getLogger(__name__)


class VisionService(BaseService):
    def __init__(self, context):
        super().__init__(context)
        self._viewport_cache = {}
        self._last_screenshot_hash = None

    async def take_screenshot(
        self,
        full_page: bool = True,
        quality: Optional[int] = 80,
        format: str = "png",
        element_selector: Optional[str] = None,
        clip_region: Optional[Dict[str, int]] = None,
        omit_background: bool = False,
        scale: str = "css",
    ) -> ServiceResult:
        try:
            tab = self.context.current_tab_or_die()

            if format not in ["png", "jpeg"]:
                return ServiceResult(
                    success=False,
                    message=f"Invalid format '{format}'. Must be 'png' or 'jpeg'",
                    error="Invalid format parameter",
                )

            if format == "jpeg" and (quality < 1 or quality > 100):
                return ServiceResult(
                    success=False,
                    message=f"Invalid quality '{quality}'. Must be between 1-100 for JPEG",
                    error="Invalid quality parameter",
                )

            screenshot_options = {
                "full_page": full_page,
                "type": format,
                "omit_background": omit_background,
            }

            if format == "jpeg":
                screenshot_options["quality"] = quality

            if clip_region:
                await self._validate_clip_region(clip_region)
                screenshot_options["clip"] = clip_region

            if element_selector:
                try:
                    element = await tab.page.wait_for_selector(
                        element_selector, timeout=5000, state="visible"
                    )
                    if not element:
                        return ServiceResult(
                            success=False,
                            message=f"Element not found: {element_selector}",
                            error="Element not found",
                        )
                    screenshot_data = await element.screenshot(**screenshot_options)
                except Exception as e:
                    return ServiceResult(
                        success=False,
                        message=f"Failed to screenshot element '{element_selector}': {str(e)}",
                        error=str(e),
                    )
            else:
                screenshot_data = await tab.page.screenshot(**screenshot_options)

            if not screenshot_data:
                return ServiceResult(
                    success=False,
                    message="Screenshot data is empty",
                    error="Empty screenshot data",
                )

            screenshot_hash = hashlib.md5(screenshot_data).hexdigest()

            content = []
            if screenshot_data:
                content.append(
                    {
                        "type": "screenshot",
                        "data": screenshot_data,
                        "url": tab.page.url,
                        "format": format,
                        "size": len(screenshot_data),
                        "hash": screenshot_hash,
                    }
                )

            success_message = f"Screenshot taken of {tab.page.url}"
            if element_selector:
                success_message += f" (element: {element_selector})"
            if clip_region:
                success_message += (
                    f" (region: {clip_region['width']}x{clip_region['height']})"
                )

            return ServiceResult(
                success=True,
                message=success_message,
                data={
                    "url": tab.page.url,
                    "full_page": full_page,
                    "format": format,
                    "quality": quality if format == "jpeg" else None,
                    "has_screenshot": True,
                    "content": content,
                    "size_bytes": len(screenshot_data),
                    "hash": screenshot_hash,
                    "element_selector": element_selector,
                    "clip_region": clip_region,
                },
            )

        except Exception as e:
            logger.error(f"Screenshot failed: {e}", exc_info=True)
            return ServiceResult(
                success=False,
                message=f"Failed to take screenshot: {str(e)}",
                error=str(e),
            )

    async def save_screenshot(
        self,
        filename: str,
        full_page: bool = True,
        quality: Optional[int] = 80,
        format: str = "png",
        element_selector: Optional[str] = None,
        clip_region: Optional[Dict[str, int]] = None,
        create_directories: bool = True,
        overwrite: bool = True,
    ) -> ServiceResult:
        try:
            screenshot_result = await self.take_screenshot(
                full_page=full_page,
                quality=quality,
                format=format,
                element_selector=element_selector,
                clip_region=clip_region,
            )

            if not screenshot_result.success:
                return screenshot_result

            screenshot_data = screenshot_result.data["content"][0]["data"]

            output_path = self.context.settings.output_dir / filename

            if create_directories:
                output_path.parent.mkdir(parents=True, exist_ok=True)

            if output_path.exists() and not overwrite:
                return ServiceResult(
                    success=False,
                    message=f"File already exists and overwrite=False: {output_path}",
                    error="File exists",
                )

            with open(output_path, "wb") as f:
                f.write(screenshot_data)

            if not output_path.exists() or output_path.stat().st_size == 0:
                return ServiceResult(
                    success=False,
                    message=f"Failed to save screenshot: file not created or empty",
                    error="File write failed",
                )

            return ServiceResult(
                success=True,
                message=f"Screenshot saved to {output_path} ({len(screenshot_data)} bytes)",
                data={
                    "filename": filename,
                    "output_path": str(output_path),
                    "full_page": full_page,
                    "format": format,
                    "size_bytes": len(screenshot_data),
                    "file_exists": True,
                },
            )

        except Exception as e:
            logger.error(f"Save screenshot failed: {e}", exc_info=True)
            return ServiceResult(
                success=False,
                message=f"Failed to save screenshot: {str(e)}",
                error=str(e),
            )

    async def screen_click(
        self,
        x: int,
        y: int,
        element: str = "",
        click_type: str = "left",
        modifiers: Optional[List[str]] = None,
        button_delay: int = 0,
        click_count: int = 1,
        force: bool = False,
        validate_bounds: bool = True,
    ) -> ServiceResult:
        try:
            tab = self.context.current_tab_or_die()

            if validate_bounds and not force:
                validation_result = await self._validate_coordinates(x, y)
                if not validation_result["valid"]:
                    return ServiceResult(
                        success=False,
                        message=f"Invalid coordinates ({x}, {y}): {validation_result['reason']}",
                        error="Invalid coordinates",
                    )

            click_options = {
                "button": self._get_mouse_button(click_type),
                "click_count": click_count,
            }

            if button_delay > 0:
                click_options["delay"] = button_delay

            if modifiers:
                for modifier in modifiers:
                    await tab.page.keyboard.down(modifier)

            try:
                if click_type == "double":
                    await tab.page.mouse.dblclick(x, y, **click_options)
                else:
                    await tab.page.mouse.click(x, y, **click_options)

                await asyncio.sleep(0.1)

            finally:
                if modifiers:
                    for modifier in reversed(modifiers):
                        await tab.page.keyboard.up(modifier)

            success_message = f"Clicked at coordinates ({x}, {y})"
            if element:
                success_message += f" - {element}"
            if click_type != "left":
                success_message += f" ({click_type} click)"
            if click_count > 1:
                success_message += f" x{click_count}"

            return ServiceResult(
                success=True,
                message=success_message,
                data={
                    "x": x,
                    "y": y,
                    "element": element,
                    "click_type": click_type,
                    "modifiers": modifiers or [],
                    "click_count": click_count,
                    "coordinates_validated": validate_bounds,
                },
            )

        except Exception as e:
            logger.error(f"Screen click failed: {e}", exc_info=True)
            return ServiceResult(
                success=False,
                message=f"Failed to click at coordinates ({x}, {y}): {str(e)}",
                error=str(e),
            )

    async def screen_drag(
        self,
        from_x: int,
        from_y: int,
        to_x: int,
        to_y: int,
        element: str = "",
        modifiers: Optional[List[str]] = None,
        steps: int = 20,
        validate_bounds: bool = True,
    ) -> ServiceResult:
        try:
            tab = self.context.current_tab_or_die()

            # Validate coordinates
            if validate_bounds:
                for coord_x, coord_y, name in [
                    (from_x, from_y, "start"),
                    (to_x, to_y, "end"),
                ]:
                    validation_result = await self._validate_coordinates(
                        coord_x, coord_y
                    )
                    if not validation_result["valid"]:
                        return ServiceResult(
                            success=False,
                            message=f"Invalid {name} coordinates ({coord_x}, {coord_y}): {validation_result['reason']}",
                            error="Invalid coordinates",
                        )

            if modifiers:
                for modifier in modifiers:
                    await tab.page.keyboard.down(modifier)

            try:
                await tab.page.mouse.move(from_x, from_y)

                await tab.page.mouse.down()

                for i in range(steps + 1):
                    progress = i / steps
                    current_x = from_x + (to_x - from_x) * progress
                    current_y = from_y + (to_y - from_y) * progress
                    await tab.page.mouse.move(current_x, current_y)
                    await asyncio.sleep(0.01)

                await tab.page.mouse.up()

            finally:
                if modifiers:
                    for modifier in reversed(modifiers):
                        await tab.page.keyboard.up(modifier)

            success_message = f"Dragged from ({from_x}, {from_y}) to ({to_x}, {to_y})"
            if element:
                success_message += f" - {element}"

            return ServiceResult(
                success=True,
                message=success_message,
                data={
                    "from_x": from_x,
                    "from_y": from_y,
                    "to_x": to_x,
                    "to_y": to_y,
                    "element": element,
                    "modifiers": modifiers or [],
                    "steps": steps,
                },
            )

        except Exception as e:
            logger.error(f"Screen drag failed: {e}", exc_info=True)
            return ServiceResult(
                success=False,
                message=f"Failed to drag from ({from_x}, {from_y}) to ({to_x}, {to_y}): {str(e)}",
                error=str(e),
            )

    async def screen_type(
        self,
        x: int,
        y: int,
        text: str,
        element: str = "",
        delay: int = 0,
        clear_first: bool = False,
        validate_bounds: bool = True,
    ) -> ServiceResult:
        try:
            tab = self.context.current_tab_or_die()

            if validate_bounds:
                validation_result = await self._validate_coordinates(x, y)
                if not validation_result["valid"]:
                    return ServiceResult(
                        success=False,
                        message=f"Invalid coordinates ({x}, {y}): {validation_result['reason']}",
                        error="Invalid coordinates",
                    )

            await tab.page.mouse.click(x, y)
            await asyncio.sleep(0.1)

            if clear_first:
                await tab.page.keyboard.press("Control+a")
                await asyncio.sleep(0.05)

            if delay > 0:
                await tab.page.keyboard.type(text, delay=delay)
            else:
                await tab.page.keyboard.type(text)

            success_message = f"Typed text at ({x}, {y}): '{text[:50]}{'...' if len(text) > 50 else ''}'"
            if element:
                success_message += f" - {element}"

            return ServiceResult(
                success=True,
                message=success_message,
                data={
                    "x": x,
                    "y": y,
                    "text": text,
                    "element": element,
                    "delay": delay,
                    "clear_first": clear_first,
                    "text_length": len(text),
                },
            )

        except Exception as e:
            logger.error(f"Screen type failed: {e}", exc_info=True)
            return ServiceResult(
                success=False,
                message=f"Failed to type at coordinates ({x}, {y}): {str(e)}",
                error=str(e),
            )

    async def move_mouse(
        self,
        x: int,
        y: int,
        element: str = "",
        steps: int = 10,
        validate_bounds: bool = True,
    ) -> ServiceResult:
        try:
            tab = self.context.current_tab_or_die()

            if validate_bounds:
                validation_result = await self._validate_coordinates(x, y)
                if not validation_result["valid"]:
                    return ServiceResult(
                        success=False,
                        message=f"Invalid coordinates ({x}, {y}): {validation_result['reason']}",
                        error="Invalid coordinates",
                    )

            await tab.page.mouse.move(x, y, steps=steps)

            success_message = f"Moved mouse to ({x}, {y})"
            if element:
                success_message += f" - {element}"

            return ServiceResult(
                success=True,
                message=success_message,
                data={"x": x, "y": y, "element": element, "steps": steps},
            )

        except Exception as e:
            logger.error(f"Move mouse failed: {e}", exc_info=True)
            return ServiceResult(
                success=False,
                message=f"Failed to move mouse to ({x}, {y}): {str(e)}",
                error=str(e),
            )

    async def capture_snapshot(self, include_screenshot: bool = True) -> ServiceResult:
        try:
            tab = self.context.current_tab_or_die()

            snapshot = await tab.capture_snapshot(include_screenshot=include_screenshot)

            if not snapshot:
                return ServiceResult(
                    success=False,
                    message="Failed to capture snapshot: snapshot is None",
                    error="Snapshot capture failed",
                )

            return ServiceResult(
                success=True,
                message="Page snapshot captured successfully",
                data={
                    "url": snapshot.url(),
                    "text": snapshot.text(),
                    "has_screenshot": snapshot.has_screenshot(),
                    "include_screenshot": include_screenshot,
                    "element_count": len(snapshot.get_all_element_references()),
                    "title": snapshot.title(),
                },
            )

        except Exception as e:
            logger.error(f"Capture snapshot failed: {e}", exc_info=True)
            return ServiceResult(
                success=False,
                message=f"Failed to capture snapshot: {str(e)}",
                error=str(e),
            )

    async def _validate_coordinates(self, x: int, y: int) -> Dict[str, Any]:
        try:
            tab = self.context.current_tab_or_die()
            viewport = await tab.page.evaluate(
                "() => ({ width: window.innerWidth, height: window.innerHeight })"
            )

            if x < 0 or y < 0:
                return {
                    "valid": False,
                    "reason": "Coordinates cannot be negative",
                    "viewport": viewport,
                }

            if x >= viewport["width"] or y >= viewport["height"]:
                return {
                    "valid": False,
                    "reason": f"Coordinates ({x}, {y}) outside viewport ({viewport['width']}x{viewport['height']})",
                    "viewport": viewport,
                }

            return {"valid": True, "viewport": viewport}

        except Exception as e:
            return {
                "valid": False,
                "reason": f"Failed to validate coordinates: {str(e)}",
                "viewport": None,
            }

    async def _validate_clip_region(self, clip_region: Dict[str, int]) -> None:
        tab = self.context.current_tab_or_die()
        viewport = await tab.page.evaluate(
            "() => ({ width: window.innerWidth, height: window.innerHeight })"
        )

        x, y, width, height = (
            clip_region["x"],
            clip_region["y"],
            clip_region["width"],
            clip_region["height"],
        )

        if x + width > viewport["width"] or y + height > viewport["height"]:
            raise ValueError(
                f"Clip region ({x}, {y}, {width}x{height}) exceeds viewport ({viewport['width']}x{viewport['height']})"
            )

    def _get_mouse_button(self, click_type: str) -> str:
        button_map = {
            "left": "left",
            "right": "right",
            "middle": "middle",
            "double": "left",
        }
        return button_map.get(click_type, "left")
