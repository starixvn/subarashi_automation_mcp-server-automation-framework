from typing import Dict, Any, Optional, TYPE_CHECKING
from .base_service import BaseService

if TYPE_CHECKING:
    from context import ServerContext
    from core.snapshot import PageSnapshot


class SnapshotService(BaseService):
    async def capture_snapshot(self, include_screenshot: bool = True) -> Dict[str, Any]:
        try:
            tab = self.get_current_tab()
            snapshot = await tab.capture_snapshot(include_screenshot=include_screenshot)

            return self.success_response(
                data={
                    "url": snapshot.url(),
                    "title": snapshot.title(),
                    "has_screenshot": snapshot.has_screenshot(),
                    "element_count": len(snapshot.get_all_element_references()),
                    "snapshot_text": snapshot.text(),
                },
                message=f"Snapshot captured for {snapshot.url()}",
            )

        except Exception as e:
            return await self.handle_error(e, "capture_snapshot")

    async def get_current_snapshot(self) -> Dict[str, Any]:
        try:
            tab = self.get_current_tab()

            if not tab.has_snapshot():
                return self.success_response(data=None, message="No snapshot available")

            snapshot = tab.get_current_snapshot()

            return self.success_response(
                data={
                    "url": snapshot.url(),
                    "title": snapshot.title(),
                    "has_screenshot": snapshot.has_screenshot(),
                    "element_count": len(snapshot.get_all_element_references()),
                    "snapshot_text": snapshot.text(),
                },
                message="Current snapshot retrieved",
            )

        except Exception as e:
            return await self.handle_error(e, "get_current_snapshot")

    async def get_element_references(self) -> Dict[str, Any]:
        try:
            tab = self.get_current_tab()

            if not tab.has_snapshot():
                return self.success_response(
                    data={"elements": []}, message="No snapshot available"
                )

            snapshot = tab.get_current_snapshot()
            element_refs = snapshot.get_all_element_references()

            elements = []
            for ref, elem in element_refs.items():
                elements.append(
                    {
                        "ref": elem.ref,
                        "element": elem.element,
                        "x": elem.x,
                        "y": elem.y,
                        "width": elem.width,
                        "height": elem.height,
                        "tag_name": elem.tag_name,
                        "text": elem.text,
                        "attributes": elem.attributes,
                    }
                )

            return self.success_response(
                data={"elements": elements, "count": len(elements)},
                message=f"Found {len(elements)} interactive elements",
            )

        except Exception as e:
            return await self.handle_error(e, "get_element_references")

    async def get_element_by_ref(self, ref: str) -> Dict[str, Any]:
        try:
            tab = self.get_current_tab()

            if not tab.has_snapshot():
                return self.success_response(data=None, message="No snapshot available")

            snapshot = tab.get_current_snapshot()
            element = snapshot.get_element_reference(ref)

            if not element:
                return self.success_response(
                    data=None, message=f"Element with ref '{ref}' not found"
                )

            return self.success_response(
                data={
                    "ref": element.ref,
                    "element": element.element,
                    "x": element.x,
                    "y": element.y,
                    "width": element.width,
                    "height": element.height,
                    "tag_name": element.tag_name,
                    "text": element.text,
                    "attributes": element.attributes,
                },
                message=f"Element found: {element.element}",
            )

        except Exception as e:
            return await self.handle_error(e, "get_element_by_ref")

    async def save_snapshot_screenshot(self, filepath: str) -> Dict[str, Any]:
        try:
            tab = self.get_current_tab()

            if not tab.has_snapshot():
                return self.success_response(
                    data={"saved": False}, message="No snapshot available"
                )

            snapshot = tab.get_current_snapshot()

            if not snapshot.has_screenshot():
                return self.success_response(
                    data={"saved": False}, message="No screenshot in snapshot"
                )

            output_path = self.get_settings().output_dir / filepath
            output_path.parent.mkdir(parents=True, exist_ok=True)

            success = await snapshot.save_screenshot(output_path)

            return self.success_response(
                data={
                    "saved": success,
                    "filepath": str(output_path) if success else None,
                },
                message=f"Screenshot {'saved' if success else 'failed to save'}",
            )

        except Exception as e:
            return await self.handle_error(e, "save_snapshot_screenshot")

    async def get_snapshot_accessibility_tree(self) -> Dict[str, Any]:
        try:
            tab = self.get_current_tab()

            if not tab.has_snapshot():
                return self.success_response(data=None, message="No snapshot available")

            snapshot = tab.get_current_snapshot()
            snapshot_dict = snapshot.to_dict()

            return self.success_response(
                data={
                    "accessibility_tree": snapshot_dict.get("accessibility_tree"),
                    "url": snapshot_dict.get("url"),
                    "title": snapshot_dict.get("title"),
                },
                message="Accessibility tree retrieved",
            )

        except Exception as e:
            return await self.handle_error(e, "get_snapshot_accessibility_tree")

    async def clear_snapshot(self) -> Dict[str, Any]:
        try:
            tab = self.get_current_tab()
            tab.clear_snapshot()

            return self.success_response(message="Snapshot cleared")

        except Exception as e:
            return await self.handle_error(e, "clear_snapshot")

    async def get_snapshot_summary(self) -> Dict[str, Any]:
        try:
            tab = self.get_current_tab()

            if not tab.has_snapshot():
                return self.success_response(
                    data={
                        "has_snapshot": False,
                        "url": tab.url(),
                        "title": await tab.title(),
                    },
                    message="No snapshot available",
                )

            snapshot = tab.get_current_snapshot()
            element_refs = snapshot.get_all_element_references()

            element_types = {}
            for elem in element_refs.values():
                tag = elem.tag_name
                element_types[tag] = element_types.get(tag, 0) + 1

            return self.success_response(
                data={
                    "has_snapshot": True,
                    "url": snapshot.url(),
                    "title": snapshot.title(),
                    "has_screenshot": snapshot.has_screenshot(),
                    "element_count": len(element_refs),
                    "element_types": element_types,
                },
                message="Snapshot summary retrieved",
            )

        except Exception as e:
            return await self.handle_error(e, "get_snapshot_summary")
