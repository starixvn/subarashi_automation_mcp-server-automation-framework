import logging
import traceback
import asyncio
import re
from datetime import datetime
from typing import Dict, Optional, List
from playwright.async_api import Page, Frame, Locator

logger = logging.getLogger(__name__)


class PageSnapshot:
    def __init__(self, page: Page):
        self.page = page
        self._aria_snapshot_text: Optional[str] = None
        self._screenshot_data: Optional[bytes] = None
        self._url: Optional[str] = None
        self._title: Optional[str] = None
        self._timestamp: Optional[str] = None
        self._last_snapshot_frame_ids: List[str] = []
        self._frame_counter: int = 0

    async def capture(
        self, include_screenshot: bool = True, timeout: float = 30000
    ) -> None:
        try:
            self._url = self.page.url
            self._title = await self.page.title()
            self._last_snapshot_frame_ids = []
            snapshot_lines = await self._snapshot_frame_for_ai(
                self.page.main_frame, 0, timeout
            )
            if isinstance(snapshot_lines, list):
                self._aria_snapshot_text = (
                    "\n".join(snapshot_lines) if snapshot_lines else ""
                )
            else:
                self._aria_snapshot_text = snapshot_lines or ""

            if include_screenshot:
                await self._capture_screenshot()

            self._timestamp = datetime.now().isoformat()

            logger.info(f"Playwright-compatible snapshot captured for URL: {self._url}")

        except Exception as e:
            logger.error(f"Critical error in snapshot capture: {type(e).__name__}: {e}")
            logger.error(f"Capture context - URL: {self._url}, Timeout: {timeout}ms")
            logger.error(f"Frame IDs tracked: {len(self._last_snapshot_frame_ids)}")

            logger.error(f"Full traceback: {traceback.format_exc()}")
            raise

    def get_snapshot_for_ai(self) -> str:
        return self._aria_snapshot_text or "No snapshot available"

    async def snapshot_for_ai(self, timeout: float = 30000) -> str:
        try:
            self._last_snapshot_frame_ids = []
            self._frame_counter = 0
            snapshot_lines = await self._snapshot_frame_for_ai(
                self.page.main_frame, 0, self._last_snapshot_frame_ids, timeout
            )
            result = "\n".join(snapshot_lines) if snapshot_lines else ""
            self._aria_snapshot_text = result
            logger.info(f"snapshotForAI captured for URL: {self.page.url}")
            return result
        except Exception as e:
            logger.error(f"snapshotForAI failed: {e}")
            raise

    async def _snapshotForAI(self) -> str:
        return await self.snapshot_for_ai()

    def ref_locator(self, params: Dict[str, str]) -> "Locator":
        ref = params.get("ref", "")

        if not ref:
            raise ValueError("Reference 'ref' parameter is required")

        current_snapshot = self._aria_snapshot_text or ""

        if not current_snapshot:
            raise ValueError(
                "No snapshot available. Please capture a snapshot first using snapshot_for_ai()."
            )

        if f"[ref={ref}]" not in current_snapshot:
            raise ValueError(
                f"Ref {ref} not found in the current page snapshot. Try capturing new snapshot."
            )

        if ref.startswith("f"):
            frame_match = re.match(r"f(\d+)e\d+", ref)
            if frame_match:
                frame_ordinal = int(frame_match.group(1))
                frames = self.page.frames

                if 0 < frame_ordinal < len(frames):
                    try:
                        target_frame = frames[frame_ordinal]
                        return target_frame.locator(f"[aria-ref='{ref}']")
                    except Exception:
                        pass

            locator = self.page.locator(f"iframe >> [aria-ref='{ref}']")
        else:
            locator = self.page.locator(f"[aria-ref='{ref}']")

        return locator

    async def ref_locators(self, params_list: list[Dict[str, str]]) -> list["Locator"]:
        snapshot = await self._snapshotForAI()
        self._aria_snapshot_text = snapshot

        locators = []
        for params in params_list:
            ref = params.get("ref", "")

            if f"[ref={ref}]" not in snapshot:
                raise ValueError(
                    f"Ref {ref} not found in the current page snapshot. Try capturing new snapshot."
                )

            locator = self.page.locator(f"[aria-ref='{ref}']")
            locators.append(locator)

        return locators

    async def _snapshot_frame_for_ai(
        self,
        frame: Frame,
        frame_ordinal: int,
        frame_ids: List[str],
        timeout: float = 30000,
    ) -> List[str]:
        try:
            retry_timeouts = [1000, 2000, 4000, 8000]
            snapshot_text = None

            for retry_timeout in retry_timeouts:
                try:
                    ref_prefix = f"f{frame_ordinal}" if frame_ordinal > 0 else ""

                    snapshot_or_retry = await frame.evaluate(
                        """
                        function(refPrefix) {
                            var node = document.body;
                            if (!node) return true;
                            
                            var refCounter = 1;
                            var elements = new Map();
                            var refs = new Map();
                            
                            function isElementVisible(el) {
                                var style = getComputedStyle(el);
                                return style.display !== 'none' && 
                                       style.visibility !== 'hidden' && 
                                       style.opacity !== '0';
                            }
                            
                            function getSemanticRole(el) {
                                var explicitRole = el.getAttribute('role');
                                if (explicitRole) return explicitRole;
                                
                                var tag = el.tagName.toLowerCase();
                                var typeMap = {
                                    'button': 'button',
                                    'input': getInputRole(el),
                                    'textarea': 'textbox',
                                    'select': 'combobox',
                                    'option': 'option',
                                    'optgroup': 'group',
                                    'a': 'link',
                                    'img': 'image',
                                    'h1': 'heading', 'h2': 'heading', 'h3': 'heading',
                                    'h4': 'heading', 'h5': 'heading', 'h6': 'heading',
                                    'p': 'paragraph',
                                    'ul': 'list', 'ol': 'list', 'dl': 'list',
                                    'li': 'listitem', 'dt': 'listitem', 'dd': 'listitem',
                                    'nav': 'navigation',
                                    'main': 'main',
                                    'aside': 'complementary',
                                    'header': 'banner',
                                    'footer': 'contentinfo',
                                    'section': 'region',
                                    'article': 'article',
                                    'iframe': 'iframe',
                                    'form': 'form',
                                    'fieldset': 'group',
                                    'legend': 'group',
                                    'label': 'generic',
                                    'table': 'table',
                                    'thead': 'rowgroup',
                                    'tbody': 'rowgroup', 
                                    'tfoot': 'rowgroup',
                                    'tr': 'row',
                                    'th': 'columnheader',
                                    'td': 'cell',
                                    'caption': 'caption',
                                    'details': 'group',
                                    'summary': 'button',
                                    'dialog': 'dialog',
                                    'menu': 'menu',
                                    'menuitem': 'menuitem',
                                    'progress': 'progressbar',
                                    'meter': 'progressbar',
                                    'time': 'time',
                                    'mark': 'mark',
                                    'code': 'code',
                                    'pre': 'code',
                                    'kbd': 'generic',
                                    'samp': 'generic',
                                    'var': 'generic',
                                    'blockquote': 'blockquote',
                                    'q': 'generic',
                                    'cite': 'generic',
                                    'abbr': 'generic',
                                    'address': 'group',
                                    'canvas': 'image',
                                    'svg': 'image',
                                    'video': 'video',
                                    'audio': 'audio',
                                    'source': 'generic',
                                    'track': 'generic',
                                    'object': 'generic',
                                    'embed': 'generic',
                                    'figure': 'figure',
                                    'figcaption': 'caption',
                                    'body': 'generic',
                                    'div': 'generic',
                                    'span': 'generic'
                                };
                                return typeMap[tag] || 'generic';
                            }
                            
                            function getInputRole(el) {
                                var type = el.type;
                                if (type === 'button' || type === 'submit') return 'button';
                                if (type === 'checkbox') return 'checkbox';
                                if (type === 'radio') return 'radio';
                                return 'textbox';
                            }
                            
                            function getAccessibleName(el) {
                                var ariaLabel = el.getAttribute('aria-label');
                                if (ariaLabel) return ariaLabel.trim();
                                
                                var ariaLabelledBy = el.getAttribute('aria-labelledby');
                                if (ariaLabelledBy) {
                                    var labelEl = document.getElementById(ariaLabelledBy);
                                    if (labelEl && labelEl.textContent) return labelEl.textContent.trim();
                                }
                                
                                var title = el.getAttribute('title');
                                if (title) return title.trim();
                                
                                var placeholder = el.getAttribute('placeholder');
                                if (placeholder) return placeholder.trim();
                                
                                var alt = el.getAttribute('alt');
                                if (alt) return alt.trim();
                                
                                var tag = el.tagName.toLowerCase();
                                if (['button', 'a', 'option'].includes(tag)) {
                                    var text = el.textContent;
                                    if (text) return text.trim();
                                }
                                
                                return '';
                            }
                            
                            function isInteractiveElement(el) {
                                var tag = el.tagName.toLowerCase();
                                var style = getComputedStyle(el);
                                return ['button', 'input', 'select', 'textarea', 'a', 'iframe'].indexOf(tag) !== -1 ||
                                       el.hasAttribute('onclick') ||
                                       el.hasAttribute('tabindex') ||
                                       el.getAttribute('role') === 'button';
                            }
                            
                            function shouldReceiveRef(el) {
                                var role = getSemanticRole(el);
                                var style = getComputedStyle(el);
                                
                                if (style.pointerEvents === 'none' || style.display === 'none') {
                                    return false;
                                }
                                
                                if (['button', 'link', 'textbox', 'combobox', 'checkbox', 'radio'].includes(role)) {
                                    return true;
                                }
                                
                                if (['heading', 'paragraph', 'image', 'table', 'list', 'listitem'].includes(role)) {
                                    return true;
                                }
                                
                                if (['navigation', 'main', 'banner', 'contentinfo', 'article', 'form'].includes(role)) {
                                    return true;
                                }
                                
                                if (role === 'iframe') {
                                    return true;
                                }
                                
                                if (role === 'generic') {
                                    var directText = '';
                                    for (var i = 0; i < el.childNodes.length; i++) {
                                        if (el.childNodes[i].nodeType === 3) { // Text node
                                            directText += el.childNodes[i].textContent || '';
                                        }
                                    }
                                    directText = directText.trim();
                                    
                                    if (directText && directText.length > 8) {
                                        var skipPatterns = ['Copyright', 'All rights reserved', 'Grand Total', 'Total in'];
                                        var hasSkipPattern = skipPatterns.some(function(pattern) {
                                            return directText.includes(pattern);
                                        });
                                        if (!hasSkipPattern) {
                                            return true;
                                        }
                                    }
                                    
                                    var interactiveChildren = el.querySelectorAll('button, a, input, select, textarea, [onclick], [role="button"]');
                                    if (interactiveChildren.length > 0) {
                                        return true;
                                    }
                                    
                                    if (style.cursor === 'pointer') {
                                        return true;
                                    }
                                    
                                    return false;
                                }
                                
                                if (['cell', 'columnheader'].includes(role)) {
                                    var cellText = el.textContent && el.textContent.trim();
                                    if (role === 'columnheader') return true;
                                    
                                    if (!cellText || cellText === '') return false;
                                    
                                    if (/^\d+$/.test(cellText)) return false;
                                    
                                    if (/^0\.0+$/.test(cellText)) return false;
                                    
                                    return cellText.length > 5;
                                }
                                
                                if (['row', 'rowgroup'].includes(role)) {
                                    return false;
                                }
                                
                                if (['region', 'section', 'complementary', 'search', 'tabpanel', 'dialog', 'alertdialog'].includes(role)) {
                                    return true;
                                }
                                
                                return false;
                            }
                            
                            function createAriaNode(el) {
                                if (!isElementVisible(el)) return null;
                                
                                var role = getSemanticRole(el);
                                var name = getAccessibleName(el);
                                var ref = null;
                                
                                if (shouldReceiveRef(el)) {
                                    ref = refPrefix + 'e' + refCounter++;
                                    el.setAttribute('aria-ref', ref);
                                    refs.set(el, ref);
                                }
                                
                                var ariaNode = {
                                    role: role,
                                    name: name,
                                    ref: ref,
                                    children: [],
                                    element: el,
                                    props: {},
                                    receivesPointerEvents: shouldReceiveRef(el),
                                    active: el === document.activeElement
                                };
                                
                                if (role === 'link' && el.hasAttribute('href')) {
                                    ariaNode.props.url = el.getAttribute('href');
                                }
                                
                                if (el.hasAttribute('checked') || el.checked) ariaNode.checked = true;
                                if (el.hasAttribute('disabled') || el.disabled) ariaNode.disabled = true;
                                
                                for (var i = 0; i < el.childNodes.length; i++) {
                                    var child = el.childNodes[i];
                                    if (child.nodeType === 3 && child.nodeValue) {
                                        var text = child.nodeValue.trim();
                                        if (text && role !== 'textbox') {
                                            ariaNode.children.push(text);
                                        }
                                    }  
                                }
                                
                                for (var i = 0; i < el.children.length; i++) {
                                    var childNode = createAriaNode(el.children[i]);
                                    if (childNode) {
                                        ariaNode.children.push(childNode);
                                    }
                                }
                                
                                return ariaNode;
                            }
                            
                            function normalizeGenericRoles(node) {
                                function normalizeChildren(node) {
                                    if (!node || !node.children) return [node];
                                    
                                    var result = [];
                                    for (var i = 0; i < node.children.length; i++) {
                                        var child = node.children[i];
                                        if (typeof child === 'string') {
                                            result.push(child);
                                            continue;
                                        }
                                        var normalized = normalizeChildren(child);
                                        for (var j = 0; j < normalized.length; j++) {
                                            result.push(normalized[j]);
                                        }
                                    }
                                    
                                    var removeSelf = node.role === 'generic' && result.length <= 1 && 
                                        result.every(function(c) { return typeof c !== 'string' && !!c.ref; });
                                    if (removeSelf) {
                                        return result;
                                    }
                                    
                                    node.children = result;
                                    return [node];
                                }
                                
                                normalizeChildren(node);
                            }
                            
                            function renderToLines(ariaNode, depth) {
                                depth = depth || 0;
                                var lines = [];
                                var indent = '  '.repeat(depth);
                                
                                var line = indent + '- ' + ariaNode.role;
                                
                                if (ariaNode.name && ariaNode.name.length > 0) {
                                    line += ' "' + ariaNode.name + '"';
                                }
                                
                                if (ariaNode.checked) line += ' [checked]';
                                if (ariaNode.disabled) line += ' [disabled]';
                                if (ariaNode.active) line += ' [active]';
                                
                                if (ariaNode.ref) {
                                    line += ' [ref=' + ariaNode.ref + ']';
                                    var style = getComputedStyle(ariaNode.element);
                                    if (style.cursor === 'pointer') {
                                        line += ' [cursor=pointer]';
                                    }
                                }
                                
                                var hasProps = ariaNode.props && Object.keys(ariaNode.props).length > 0;
                                var hasChildren = ariaNode.children && ariaNode.children.length > 0;
                                
                                if (!hasChildren && !hasProps) {
                                    lines.push(line);
                                } else if (hasChildren && ariaNode.children.length === 1 && typeof ariaNode.children[0] === 'string' && !hasProps) {
                                    var text = ariaNode.children[0];
                                    lines.push(line + ': ' + text);
                                } else {
                                    lines.push(line + ':');
                                    
                                    if (hasProps) {
                                        for (var prop in ariaNode.props) {
                                            lines.push(indent + '  - /' + prop + ': ' + ariaNode.props[prop]);
                                        }
                                    }
                                    
                                    if (hasChildren) {
                                        for (var i = 0; i < ariaNode.children.length; i++) {
                                            var child = ariaNode.children[i];
                                            if (typeof child === 'string') {
                                                lines.push(indent + '  - text: ' + child);
                                            } else {
                                                var childLines = renderToLines(child, depth + 1);
                                                for (var j = 0; j < childLines.length; j++) {
                                                    lines.push(childLines[j]);
                                                }
                                            }
                                        }
                                    }
                                }
                                
                                return lines;
                            }
                            
                            var rootNode = createAriaNode(node);
                            if (!rootNode) return '';
                            
                            normalizeGenericRoles(rootNode);
                            var lines = renderToLines(rootNode);
                            
                            return lines.join('\\n');
                        }
                        """,
                        ref_prefix,
                    )

                    if snapshot_or_retry is not True:
                        snapshot_text = snapshot_or_retry
                        break

                    await asyncio.sleep(retry_timeout / 1000)

                except Exception as e:
                    if self._is_non_retriable_error(e):
                        raise
                    if retry_timeout == retry_timeouts[-1]:
                        raise
                    await asyncio.sleep(retry_timeout / 1000)

            if not snapshot_text:
                return []

            lines = snapshot_text.split("\n")
            result = []

            for line in lines:
                iframe_match = re.match(
                    r"^(\s*)- iframe (?:\[active\] )?\[ref=([^\]]*)\](.*)$", line
                )
                if iframe_match:
                    leading_space = iframe_match.group(1)
                    ref = iframe_match.group(2)

                    result.append(line)

                    try:
                        iframe_content = (
                            await self._capture_iframe_content_typescript_style(
                                frame, ref, frame_ordinal, frame_ids
                            )
                        )
                        if iframe_content:
                            for content_line in iframe_content:
                                indented_line = leading_space + "  " + content_line
                                result.append(indented_line)
                    except Exception as e:
                        logger.warning(
                            f"Failed to capture iframe content for {ref}: {e}"
                        )
                        pass
                else:
                    result.append(line)

            return result

        except Exception as e:
            logger.error(f"Error in _snapshot_frame_for_ai: {e}")
            if self._is_non_retriable_error(e):
                raise
            return []

    async def _capture_iframe_content_typescript_style(
        self,
        parent_frame: Frame,
        iframe_ref: str,
        parent_frame_ordinal: int,
        frame_ids: List[str],
    ) -> List[str]:
        try:
            try:
                iframe_locator = parent_frame.locator(f"[aria-ref='{iframe_ref}']")
                iframe_element = await iframe_locator.element_handle(timeout=2000)
                if not iframe_element:
                    return []

                content_frame = await iframe_element.content_frame()
                if not content_frame:
                    return []

            except Exception:
                try:
                    frame_locator = parent_frame.frame_locator(
                        f"[aria-ref='{iframe_ref}']"
                    )
                    await frame_locator.locator("body").count()
                    return []
                except Exception:
                    return []

            frame_ordinal = len(frame_ids) + 1

            try:
                frame_id = getattr(content_frame, "_guid", content_frame.url)
                frame_ids.append(frame_id)
                logger.debug(f"Added frame ID: {frame_id}")
            except Exception as e:
                logger.warning(f"Failed to get frame ID: {e}, using URL instead")
                frame_ids.append(content_frame.url)

            try:
                child_snapshot = await self._snapshot_frame_for_ai(
                    content_frame, frame_ordinal, frame_ids
                )
                return child_snapshot

            except Exception as e:
                logger.warning(f"Failed to capture iframe snapshot: {e}")
                return []

        except Exception as e:
            logger.warning(f"Error capturing iframe content for {iframe_ref}: {e}")
            return []

    def get_last_snapshot_frame_ids(self) -> List[str]:
        return self._last_snapshot_frame_ids.copy()

    def to_dict(self) -> dict:
        return {
            "url": self._url,
            "title": self._title,
            "timestamp": self._timestamp,
            "has_screenshot": self.has_screenshot,
        }

    def _is_non_retriable_error(self, error: Exception) -> bool:
        error_str = str(error).lower()

        non_retriable_patterns = [
            "page closed",
            "page crashed",
            "context closed",
            "browser closed",
            "navigation failed",
            "net::err_aborted",
        ]

        return any(pattern in error_str for pattern in non_retriable_patterns)

    async def _capture_screenshot(self) -> None:
        try:
            self._screenshot_data = await self.page.screenshot(full_page=True)
            logger.debug("Screenshot captured successfully")
        except Exception as e:
            logger.error(f"Error capturing screenshot: {e}")
            self._screenshot_data = None

    @property
    def url(self) -> Optional[str]:
        return self._url

    @property
    def title(self) -> Optional[str]:
        return self._title

    @property
    def has_screenshot(self) -> bool:
        return self._screenshot_data is not None

    def get_screenshot_data(self) -> Optional[bytes]:
        return self._screenshot_data

    def get_all_element_references(self) -> dict:
        return {}

    def get_element_reference(self, ref: str) -> Optional[dict]:
        return None

    async def save_screenshot(self, filepath: str) -> bool:
        try:
            if not self._screenshot_data:
                await self._capture_screenshot()

            if self._screenshot_data:
                with open(filepath, "wb") as f:
                    f.write(self._screenshot_data)
                return True
            return False
        except Exception as e:
            logger.error(f"Error saving screenshot: {e}")
            return False

    def text(self) -> str:
        return self._aria_snapshot_text or ""
