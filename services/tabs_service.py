from typing import Dict, Any, Optional, List, TYPE_CHECKING
from .base_service import BaseService

if TYPE_CHECKING:
    from context import ServerContext


class TabsService(BaseService):
    async def list_tabs(self) -> Dict[str, Any]:
        try:
            await self.ensure_tab()

            tabs = self.context.tabs()
            tab_list = []

            for i, tab in enumerate(tabs):
                tab_info = {
                    "index": i,
                    "url": tab.url(),
                    "title": await tab.title(),
                    "is_current": tab == self.context._current_tab,
                }
                tab_list.append(tab_info)

            return self.success_response(
                data={
                    "tabs": tab_list,
                    "count": len(tab_list),
                    "current_index": self.context._current_tab_index
                    if hasattr(self.context, "_current_tab_index")
                    else 0,
                },
                message=f"Found {len(tab_list)} tabs",
            )

        except Exception as e:
            return await self.handle_error(e, "list_tabs")

    async def create_new_tab(self, url: Optional[str] = None) -> Dict[str, Any]:
        try:
            tab = await self.context.new_tab()

            if url:
                final_url = await tab.navigate(url)
                message = f"Created new tab and navigated to {final_url}"
            else:
                final_url = tab.url()
                message = "Created new tab"

            return self.success_response(
                data={
                    "url": final_url,
                    "title": await tab.title(),
                    "tab_count": len(self.context.tabs()),
                },
                message=message,
            )

        except Exception as e:
            return await self.handle_error(e, "create_new_tab")

    async def select_tab(self, index: int) -> Dict[str, Any]:
        try:
            await self.context.select_tab(index)

            current_tab = self.get_current_tab()

            return self.success_response(
                data={
                    "index": index,
                    "url": current_tab.url(),
                    "title": await current_tab.title(),
                },
                message=f"Selected tab {index}",
            )

        except Exception as e:
            return await self.handle_error(e, "select_tab")

    async def close_tab(self, index: Optional[int] = None) -> Dict[str, Any]:
        try:
            if index is not None:
                await self.context.close_tab(index)
                message = f"Closed tab {index}"
            else:
                await self.context.close_tab()
                message = "Closed current tab"

            remaining_tabs = len(self.context.tabs())

            return self.success_response(
                data={"remaining_tabs": remaining_tabs, "closed_index": index},
                message=message,
            )

        except Exception as e:
            return await self.handle_error(e, "close_tab")

    async def get_current_tab_info(self) -> Dict[str, Any]:
        try:
            tab = self.get_current_tab()

            return self.success_response(
                data={
                    "url": tab.url(),
                    "title": await tab.title(),
                    "has_snapshot": tab.has_snapshot(),
                    "console_messages": len(tab.get_console_messages()),
                    "network_requests": len(tab.get_network_requests()),
                },
                message="Current tab info retrieved",
            )

        except Exception as e:
            return await self.handle_error(e, "get_current_tab_info")

    async def get_tab_console_messages(
        self, index: Optional[int] = None
    ) -> Dict[str, Any]:
        try:
            if index is not None:
                tabs = self.context.tabs()
                if index >= len(tabs):
                    return self.success_response(
                        data={"messages": []}, message=f"Tab {index} not found"
                    )
                tab = tabs[index]
            else:
                tab = self.get_current_tab()

            messages = tab.get_console_messages()

            return self.success_response(
                data={"messages": messages, "count": len(messages)},
                message=f"Found {len(messages)} console messages",
            )

        except Exception as e:
            return await self.handle_error(e, "get_tab_console_messages")

    async def get_tab_network_requests(
        self, index: Optional[int] = None
    ) -> Dict[str, Any]:
        try:
            if index is not None:
                tabs = self.context.tabs()
                if index >= len(tabs):
                    return self.success_response(
                        data={"requests": []}, message=f"Tab {index} not found"
                    )
                tab = tabs[index]
            else:
                tab = self.get_current_tab()

            requests = tab.get_network_requests()

            return self.success_response(
                data={"requests": requests, "count": len(requests)},
                message=f"Found {len(requests)} network requests",
            )

        except Exception as e:
            return await self.handle_error(e, "get_tab_network_requests")

    async def clear_tab_console_messages(
        self, index: Optional[int] = None
    ) -> Dict[str, Any]:
        try:
            if index is not None:
                tabs = self.context.tabs()
                if index >= len(tabs):
                    return self.success_response(
                        data={"cleared": False}, message=f"Tab {index} not found"
                    )
                tab = tabs[index]
            else:
                tab = self.get_current_tab()

            tab.clear_console_messages()

            return self.success_response(
                data={"cleared": True}, message="Console messages cleared"
            )

        except Exception as e:
            return await self.handle_error(e, "clear_tab_console_messages")

    async def clear_tab_network_requests(
        self, index: Optional[int] = None
    ) -> Dict[str, Any]:
        try:
            if index is not None:
                tabs = self.context.tabs()
                if index >= len(tabs):
                    return self.success_response(
                        data={"cleared": False}, message=f"Tab {index} not found"
                    )
                tab = tabs[index]
            else:
                tab = self.get_current_tab()

            tab.clear_network_requests()

            return self.success_response(
                data={"cleared": True}, message="Network requests cleared"
            )

        except Exception as e:
            return await self.handle_error(e, "clear_tab_network_requests")

    async def duplicate_tab(self, index: Optional[int] = None) -> Dict[str, Any]:
        try:
            if index is not None:
                tabs = self.context.tabs()
                if index >= len(tabs):
                    return self.success_response(
                        data={"duplicated": False}, message=f"Tab {index} not found"
                    )
                source_tab = tabs[index]
            else:
                source_tab = self.get_current_tab()

            new_tab = await self.context.new_tab()
            source_url = source_tab.url()

            if source_url and source_url != "about:blank":
                await new_tab.navigate(source_url)

            return self.success_response(
                data={
                    "duplicated": True,
                    "original_url": source_url,
                    "new_tab_url": new_tab.url(),
                    "total_tabs": len(self.context.tabs()),
                },
                message=f"Duplicated tab to {new_tab.url()}",
            )

        except Exception as e:
            return await self.handle_error(e, "duplicate_tab")

    async def get_tabs_summary(self) -> Dict[str, Any]:
        try:
            tabs = self.context.tabs()
            tabs_info = []

            for i, tab in enumerate(tabs):
                tab_info = {
                    "index": i,
                    "url": tab.url(),
                    "title": await tab.title(),
                    "is_current": tab == self.context._current_tab,
                    "has_snapshot": tab.has_snapshot(),
                    "console_count": len(tab.get_console_messages()),
                    "network_count": len(tab.get_network_requests()),
                }
                tabs_info.append(tab_info)

            return self.success_response(
                data={
                    "tabs": tabs_info,
                    "total_count": len(tabs_info),
                    "current_index": next(
                        (i for i, t in enumerate(tabs_info) if t["is_current"]), 0
                    ),
                },
                message=f"Tabs summary: {len(tabs_info)} tabs",
            )

        except Exception as e:
            return await self.handle_error(e, "get_tabs_summary")
