from typing import Dict, Any, Optional
from .base_service import BaseService, ServiceResult


class VisionService(BaseService):
    def __init__(self, context):
        super().__init__(context)

    async def take_screenshot(self, full_page: bool = False) -> ServiceResult:
        try:
            tab = self.context.current_tab_or_die()

            snapshot = await tab.capture_snapshot(include_screenshot=True)

            content = []
            if snapshot.has_screenshot():
                content.append(
                    {
                        "type": "screenshot",
                        "data": snapshot.get_screenshot_data(),
                        "url": snapshot.url(),
                    }
                )

            return ServiceResult(
                success=True,
                message=f"Screenshot taken of {snapshot.url()}",
                data={
                    "url": snapshot.url(),
                    "full_page": full_page,
                    "has_screenshot": snapshot.has_screenshot(),
                    "content": content,
                },
            )
        except Exception as e:
            return ServiceResult(
                success=False,
                message=f"Failed to take screenshot: {str(e)}",
                error=str(e),
            )

    async def save_screenshot(
        self, filename: str, full_page: bool = False
    ) -> ServiceResult:
        try:
            tab = self.context.current_tab_or_die()

            snapshot = await tab.capture_snapshot(include_screenshot=True)
            output_path = self.context.settings.output_dir / filename

            success = await snapshot.save_screenshot(output_path)

            if success:
                return ServiceResult(
                    success=True,
                    message=f"Screenshot saved to {output_path}",
                    data={
                        "filename": filename,
                        "output_path": str(output_path),
                        "full_page": full_page,
                    },
                )
            else:
                return ServiceResult(
                    success=False,
                    message=f"Failed to save screenshot to {output_path}",
                    error="Could not save screenshot file",
                )
        except Exception as e:
            return ServiceResult(
                success=False,
                message=f"Failed to save screenshot: {str(e)}",
                error=str(e),
            )

    async def screen_click(self, x: int, y: int, element: str = "") -> ServiceResult:
        try:
            tab = self.context.current_tab_or_die()

            await tab.page.mouse.click(x, y)

            return ServiceResult(
                success=True,
                message=f"Clicked at coordinates ({x}, {y}){' - ' + element if element else ''}",
                data={"x": x, "y": y, "element": element},
            )
        except Exception as e:
            return ServiceResult(
                success=False,
                message=f"Failed to click at coordinates ({x}, {y}): {str(e)}",
                error=str(e),
            )

    async def capture_snapshot(self, include_screenshot: bool = True) -> ServiceResult:
        try:
            tab = self.context.current_tab_or_die()

            snapshot = await tab.capture_snapshot(include_screenshot=include_screenshot)

            return ServiceResult(
                success=True,
                message="Page snapshot captured",
                data={
                    "url": snapshot.url(),
                    "text": snapshot.text(),
                    "has_screenshot": snapshot.has_screenshot(),
                    "include_screenshot": include_screenshot,
                },
            )
        except Exception as e:
            return ServiceResult(
                success=False,
                message=f"Failed to capture snapshot: {str(e)}",
                error=str(e),
            )
