from typing import Dict, Any
from .base_service import BaseService


class CoreService(BaseService):
    async def close_browser(self) -> Dict[str, Any]:
        try:
            await self.context.close()
            return self.success_response(message="Browser closed successfully")
        except Exception as e:
            return await self.handle_error(e, "close_browser")

    async def navigate_to_url(self, url: str) -> Dict[str, Any]:
        try:
            tab = await self.ensure_tab()
            final_url = await tab.navigate(url)

            return self.success_response(
                data={"url": final_url}, message=f"Navigated to {final_url}"
            )
        except Exception as e:
            return await self.handle_error(e, "navigate_to_url")

    async def resize_browser(self, width: int, height: int) -> Dict[str, Any]:
        try:
            tab = self.get_current_tab()

            await tab.page.set_viewport_size({"width": width, "height": height})

            return self.success_response(
                data={"width": width, "height": height},
                message=f"Browser resized to {width}x{height}",
            )
        except Exception as e:
            return await self.handle_error(e, "resize_browser")

    async def go_back(self) -> Dict[str, Any]:
        try:
            tab = await self.ensure_tab()
            await tab.page.go_back()

            return self.success_response(
                data={"url": tab.url()}, message="Navigated back"
            )
        except Exception as e:
            return await self.handle_error(e, "go_back")

    async def go_forward(self) -> Dict[str, Any]:
        try:
            tab = self.get_current_tab()
            await tab.page.go_forward()

            return self.success_response(
                data={"url": tab.url()}, message="Navigated forward"
            )
        except Exception as e:
            return await self.handle_error(e, "go_forward")

    async def get_current_url(self) -> Dict[str, Any]:
        try:
            tab = self.get_current_tab()
            url = tab.url()

            return self.success_response(
                data={"url": url}, message=f"Current URL: {url}"
            )
        except Exception as e:
            return await self.handle_error(e, "get_current_url")

    async def get_page_title(self) -> Dict[str, Any]:
        try:
            tab = self.get_current_tab()
            title = await tab.title()

            return self.success_response(
                data={"title": title}, message=f"Page title: {title}"
            )
        except Exception as e:
            return await self.handle_error(e, "get_page_title")

    async def reload_page(self) -> Dict[str, Any]:
        try:
            tab = self.get_current_tab()
            await tab.reload()

            return self.success_response(
                data={"url": tab.url()}, message="Page reloaded"
            )
        except Exception as e:
            return await self.handle_error(e, "reload_page")
