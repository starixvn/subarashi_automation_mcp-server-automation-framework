import base64
import json
import logging
from typing import Dict, Any, List, Optional, Tuple, TYPE_CHECKING
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

if TYPE_CHECKING:
    from playwright.async_api import Page, Locator

logger = logging.getLogger(__name__)


@dataclass
class ElementReference:

    ref: str
    element: str
    x: int
    y: int
    width: int
    height: int
    tag_name: str
    text: Optional[str] = None
    attributes: Optional[Dict[str, str]] = None


@dataclass
class AccessibilityNode:

    role: str
    name: Optional[str] = None
    value: Optional[str] = None
    description: Optional[str] = None
    keyshortcuts: Optional[str] = None
    roledescription: Optional[str] = None
    valuetext: Optional[str] = None
    disabled: bool = False
    expanded: Optional[bool] = None
    focused: bool = False
    modal: bool = False
    multiline: bool = False
    multiselectable: bool = False
    readonly: bool = False
    required: bool = False
    selected: Optional[bool] = None
    checked: Optional[bool] = None
    pressed: Optional[bool] = None
    level: Optional[int] = None
    valuemin: Optional[float] = None
    valuemax: Optional[float] = None
    autocomplete: Optional[str] = None
    haspopup: Optional[str] = None
    invalid: Optional[str] = None
    orientation: Optional[str] = None
    children: List["AccessibilityNode"] = None

    def __post_init__(self):
        if self.children is None:
            self.children = []


class PageSnapshot:

    def __init__(self, page: "Page"):
        self.page = page
        self._accessibility_tree: Optional[AccessibilityNode] = None
        self._element_references: Dict[str, ElementReference] = {}
        self._screenshot_data: Optional[bytes] = None
        self._page_text: Optional[str] = None
        self._url: Optional[str] = None
        self._title: Optional[str] = None
        self._timestamp: Optional[str] = None

    async def capture(self, include_screenshot: bool = True) -> None:
        logger.debug("Capturing page snapshot")

        try:
            self._url = self.page.url
            self._title = await self.page.title()

            await self._capture_accessibility_tree()

            await self._capture_element_references()

            if include_screenshot:
                await self._capture_screenshot()

            await self._capture_page_text()

            self._timestamp = datetime.now().isoformat()

            logger.info(
                f"Snapshot captured: {len(self._element_references)} elements, URL: {self._url}"
            )

        except Exception as e:
            logger.error(f"Error capturing snapshot: {e}")
            raise

    async def _capture_accessibility_tree(self) -> None:
        try:
            accessibility_tree = await self.page.accessibility.snapshot(
                interesting_only=True, root=None
            )

            if accessibility_tree:
                self._accessibility_tree = self._convert_accessibility_node(
                    accessibility_tree
                )

        except Exception as e:
            logger.warning(f"Failed to capture accessibility tree: {e}")
            self._accessibility_tree = None

    def _convert_accessibility_node(self, node: Dict[str, Any]) -> AccessibilityNode:
        children = []
        if "children" in node:
            children = [
                self._convert_accessibility_node(child) for child in node["children"]
            ]

        return AccessibilityNode(
            role=node.get("role", ""),
            name=node.get("name"),
            value=node.get("value"),
            description=node.get("description"),
            keyshortcuts=node.get("keyshortcuts"),
            roledescription=node.get("roledescription"),
            valuetext=node.get("valuetext"),
            disabled=node.get("disabled", False),
            expanded=node.get("expanded"),
            focused=node.get("focused", False),
            modal=node.get("modal", False),
            multiline=node.get("multiline", False),
            multiselectable=node.get("multiselectable", False),
            readonly=node.get("readonly", False),
            required=node.get("required", False),
            selected=node.get("selected"),
            checked=node.get("checked"),
            pressed=node.get("pressed"),
            level=node.get("level"),
            valuemin=node.get("valuemin"),
            valuemax=node.get("valuemax"),
            autocomplete=node.get("autocomplete"),
            haspopup=node.get("haspopup"),
            invalid=node.get("invalid"),
            orientation=node.get("orientation"),
            children=children,
        )

    async def _capture_element_references(self) -> None:
        try:
            js_code = """
            () => {
                const elements = [];
                const interactiveSelectors = [
                    'a', 'button', 'input', 'select', 'textarea', 'label',
                    '[onclick]', '[role="button"]', '[role="link"]', '[role="tab"]',
                    '[role="menuitem"]', '[role="option"]', '[tabindex]'
                ];
                
                const allElements = document.querySelectorAll(interactiveSelectors.join(', '));
                
                allElements.forEach((el, index) => {
                    const rect = el.getBoundingClientRect();
                    if (rect.width > 0 && rect.height > 0) {
                        const ref = `element_${index}`;
                        el.setAttribute('data-ref', ref);
                        
                        elements.push({
                            ref: ref,
                            element: el.tagName.toLowerCase() + (el.textContent ? ': ' + el.textContent.trim().substring(0, 50) : ''),
                            x: Math.round(rect.left + rect.width / 2),
                            y: Math.round(rect.top + rect.height / 2),
                            width: Math.round(rect.width),
                            height: Math.round(rect.height),
                            tag_name: el.tagName.toLowerCase(),
                            text: el.textContent ? el.textContent.trim() : null,
                            attributes: {
                                id: el.id || null,
                                class: el.className || null,
                                type: el.type || null,
                                href: el.href || null,
                                role: el.getAttribute('role') || null
                            }
                        });
                    }
                });
                
                return elements;
            }
            """

            elements_data = await self.page.evaluate(js_code)

            self._element_references = {}
            for elem_data in elements_data:
                ref = ElementReference(
                    ref=elem_data["ref"],
                    element=elem_data["element"],
                    x=elem_data["x"],
                    y=elem_data["y"],
                    width=elem_data["width"],
                    height=elem_data["height"],
                    tag_name=elem_data["tag_name"],
                    text=elem_data["text"],
                    attributes=elem_data["attributes"],
                )
                self._element_references[ref.ref] = ref

        except Exception as e:
            logger.warning(f"Failed to capture element references: {e}")
            self._element_references = {}

    async def _capture_screenshot(self) -> None:
        try:
            self._screenshot_data = await self.page.screenshot(
                full_page=True, type="png"
            )
        except Exception as e:
            logger.warning(f"Failed to capture screenshot: {e}")
            self._screenshot_data = None

    async def _capture_page_text(self) -> None:
        try:
            self._page_text = await self.page.evaluate("() => document.body.innerText")
        except Exception as e:
            logger.warning(f"Failed to capture page text: {e}")
            self._page_text = ""

    def url(self) -> Optional[str]:
        return self._url

    def title(self) -> Optional[str]:
        return self._title

    def text(self) -> str:
        if not self._accessibility_tree and not self._page_text:
            return "No snapshot data available"

        lines = []

        if self._url:
            lines.append(f"Page URL: {self._url}")
        if self._title:
            lines.append(f"Page Title: {self._title}")
        lines.append("")

        if self._accessibility_tree:
            lines.append("Accessibility Tree:")
            lines.extend(self._format_accessibility_tree(self._accessibility_tree))
            lines.append("")

        if self._element_references:
            lines.append("Interactive Elements:")
            for ref, elem in self._element_references.items():
                lines.append(f"  [{ref}] {elem.element} at ({elem.x}, {elem.y})")
            lines.append("")

        if not self._accessibility_tree and self._page_text:
            lines.append("Page Text:")
            lines.append(self._page_text[:2000])  # Limit text length

        return "\n".join(lines)

    def _format_accessibility_tree(
        self, node: AccessibilityNode, indent: int = 0
    ) -> List[str]:
        lines = []
        prefix = "  " * indent

        node_info = f"{prefix}{node.role}"
        if node.name:
            node_info += f": {node.name}"
        if node.value:
            node_info += f" = {node.value}"

        lines.append(node_info)

        for child in node.children:
            lines.extend(self._format_accessibility_tree(child, indent + 1))

        return lines

    def get_element_reference(self, ref: str) -> Optional[ElementReference]:
        return self._element_references.get(ref)

    def get_all_element_references(self) -> Dict[str, ElementReference]:
        return self._element_references.copy()

    def ref_locator(self, params: Dict[str, str]) -> "Locator":
        element = params.get("element", "")
        ref = params.get("ref", "")

        locator = self.page.locator(f"[data-ref='{ref}']")

        return locator

    def has_screenshot(self) -> bool:
        return self._screenshot_data is not None

    def get_screenshot_data(self) -> Optional[bytes]:
        return self._screenshot_data

    async def save_screenshot(self, path: Path) -> bool:
        if not self._screenshot_data:
            return False

        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "wb") as f:
                f.write(self._screenshot_data)
            return True
        except Exception as e:
            logger.error(f"Failed to save screenshot: {e}")
            return False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "url": self._url,
            "title": self._title,
            "timestamp": self._timestamp,
            "has_screenshot": self.has_screenshot(),
            "element_count": len(self._element_references),
            "accessibility_tree": (
                self._accessibility_tree_to_dict() if self._accessibility_tree else None
            ),
            "element_references": {
                ref: {
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
                for ref, elem in self._element_references.items()
            },
        }

    def _accessibility_tree_to_dict(self) -> Dict[str, Any]:
        def node_to_dict(node: AccessibilityNode) -> Dict[str, Any]:
            return {
                "role": node.role,
                "name": node.name,
                "value": node.value,
                "description": node.description,
                "children": [node_to_dict(child) for child in node.children],
            }

        return node_to_dict(self._accessibility_tree)

    def __str__(self) -> str:
        return (
            f"PageSnapshot(url={self._url}, elements={len(self._element_references)})"
        )
