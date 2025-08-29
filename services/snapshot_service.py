from typing import Dict, Any, List
from .base_service import BaseService
from core.snapshot import PageSnapshot


class SnapshotService(BaseService):
    async def capture_snapshot_for_ai(self, timeout: float = 30000) -> Dict[str, Any]:
        try:
            tab = self.get_current_tab()
            page = tab.page
            snapshot_obj = PageSnapshot(page)
            aria_snapshot = await snapshot_obj.snapshot_for_ai(timeout=timeout)
            refs_found = self._extract_refs_from_aria_snapshot(aria_snapshot)

            return self.success_response(
                data={
                    "url": page.url,
                    "title": await page.title(),
                    "snapshot_text": aria_snapshot,
                    "element_count": len(refs_found["main_refs"])
                    + len(refs_found["iframe_refs"]),
                    "main_elements_count": len(refs_found["main_refs"]),
                    "iframe_elements_count": len(refs_found["iframe_refs"]),
                    "refs_found": refs_found,
                    "frames_processed": snapshot_obj.get_last_snapshot_frame_ids(),
                },
                message=f"AI snapshot captured for {page.url} (Elements: {len(refs_found['main_refs'])} main + {len(refs_found['iframe_refs'])} iframe)",
            )

        except Exception as e:
            return await self.handle_error(e, "capture_snapshot_for_ai")

    async def capture_snapshot(self, tab_id: str = None) -> Dict[str, Any]:
        try:
            if tab_id:
                tab = self.context.get_tab(tab_id)
                if not tab:
                    return self.error_response(f"Tab {tab_id} not found")
            else:
                tab = self.get_current_tab()

            page = tab.page
            snapshot_obj = PageSnapshot(page)
            aria_snapshot = await snapshot_obj.snapshot_for_ai()
            tab.snapshot = snapshot_obj
            refs_found = self._extract_refs_from_aria_snapshot(aria_snapshot)

            return self.success_response(
                data={
                    "snapshot_text": aria_snapshot,
                    "url": page.url,
                    "title": await page.title(),
                    "element_count": len(refs_found["main_refs"])
                    + len(refs_found["iframe_refs"]),
                }
            )
        except Exception as e:
            return self.error_response(str(e))

    async def get_current_snapshot(self) -> Dict[str, Any]:
        try:
            return await self.capture_snapshot_for_ai()
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

            output_path = self.get_config().output_dir / filepath
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
                    "url": snapshot.url,
                    "title": snapshot.title,
                    "has_screenshot": snapshot.has_screenshot,
                    "element_count": len(element_refs),
                    "element_types": element_types,
                },
                message="Snapshot summary retrieved",
            )

        except Exception as e:
            return await self.handle_error(e, "get_snapshot_summary")

    def _categorize_elements(self, element_refs: Dict[str, Any]) -> Dict[str, Any]:
        categories = {
            "form_inputs": [],
            "buttons": [],
            "links": [],
            "navigation": [],
            "headings": [],
            "interactive_content": [],
            "media": [],
            "custom_controls": [],
            "accessibility_elements": [],
        }

        for ref, elem in element_refs.items():
            tag = (elem.tag_name or "").lower()
            attrs = elem.attributes or {}
            element_type = (attrs.get("type") or "").lower()
            role = (attrs.get("role") or "").lower()

            if tag == "input":
                categories["form_inputs"].append(
                    {
                        "ref": elem.ref,
                        "description": elem.element,
                        "type": element_type,
                        "required": attrs.get("required", False),
                        "disabled": attrs.get("disabled", False),
                    }
                )
            elif tag == "button" or element_type in ["button", "submit", "reset"]:
                categories["buttons"].append(
                    {
                        "ref": elem.ref,
                        "description": elem.element,
                        "type": element_type or "button",
                        "disabled": attrs.get("disabled", False),
                    }
                )
            elif tag == "a" or role == "link":
                categories["links"].append(
                    {
                        "ref": elem.ref,
                        "description": elem.element,
                        "href": attrs.get("href"),
                        "target": attrs.get("target"),
                    }
                )
            elif tag in ["nav"] or role in ["navigation", "menu", "menubar"]:
                categories["navigation"].append(
                    {"ref": elem.ref, "description": elem.element, "role": role or tag}
                )
            elif tag in ["h1", "h2", "h3", "h4", "h5", "h6"]:
                categories["headings"].append(
                    {"ref": elem.ref, "description": elem.element, "level": tag}
                )
            elif tag in ["select", "textarea", "label"]:
                categories["form_inputs"].append(
                    {
                        "ref": elem.ref,
                        "description": elem.element,
                        "type": tag,
                        "required": attrs.get("required", False),
                        "disabled": attrs.get("disabled", False),
                    }
                )
            elif tag in ["video", "audio", "embed", "object"]:
                categories["media"].append(
                    {"ref": elem.ref, "description": elem.element, "type": tag}
                )
            elif role in ["button", "tab", "menuitem", "option", "slider", "switch"]:
                categories["custom_controls"].append(
                    {
                        "ref": elem.ref,
                        "description": elem.element,
                        "role": role,
                        "aria_label": attrs.get("aria-label"),
                    }
                )
            elif attrs.get("aria-label") or attrs.get("aria-labelledby"):
                categories["accessibility_elements"].append(
                    {
                        "ref": elem.ref,
                        "description": elem.element,
                        "aria_label": attrs.get("aria-label"),
                        "aria_labelledby": attrs.get("aria-labelledby"),
                    }
                )
            else:
                categories["interactive_content"].append(
                    {
                        "ref": elem.ref,
                        "description": elem.element,
                        "tag": tag,
                        "role": role,
                    }
                )

        category_summary = {
            category: len(items) for category, items in categories.items()
        }

        return {"summary": category_summary, "details": categories}

    def _get_detailed_element_info(
        self, element_refs: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        detailed_elements = []

        for ref, elem in element_refs.items():
            attrs = elem.attributes or {}

            element_info = {
                "ref": elem.ref,
                "description": elem.element,
                "position": {"x": elem.x, "y": elem.y},
                "size": {"width": elem.width, "height": elem.height},
                "tag": elem.tag_name,
                "text": elem.text,
                "key_attributes": {
                    "id": attrs.get("id"),
                    "class": attrs.get("class"),
                    "type": attrs.get("type"),
                    "name": attrs.get("name"),
                    "placeholder": attrs.get("placeholder"),
                    "role": attrs.get("role"),
                    "aria_label": attrs.get("aria-label"),
                    "disabled": attrs.get("disabled", False),
                    "required": attrs.get("required", False),
                    "visible": attrs.get("visible", True),
                    "focusable": attrs.get("focusable", False),
                },
                "iframe_context": {
                    "is_iframe": elem.iframe_index is not None,
                    "iframe_index": elem.iframe_index,
                    "iframe_selector": elem.iframe_selector,
                },
            }

            detailed_elements.append(element_info)

        return detailed_elements

    def _extract_refs_from_aria_snapshot(
        self, aria_snapshot: str
    ) -> Dict[str, List[str]]:
        import re

        main_refs = []
        iframe_refs = []
        ref_pattern = r"\[ref=([^\]]+)\]"
        refs = re.findall(ref_pattern, aria_snapshot)

        for ref in refs:
            if ref.startswith("f"):
                iframe_refs.append(ref)
            else:
                main_refs.append(ref)

        return {"main_refs": main_refs, "iframe_refs": iframe_refs, "all_refs": refs}
