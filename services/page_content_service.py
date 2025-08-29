from typing import Dict, Any, Optional
from .base_service import BaseService

try:
    from bs4 import BeautifulSoup
except ImportError:
    BeautifulSoup = None


class PageContentService(BaseService):
    def _format_html(self, html_content: str) -> str:
        try:
            if BeautifulSoup:
                soup = BeautifulSoup(html_content, "html.parser")
                return soup.prettify()
            else:
                html_content = html_content.replace("><", ">\n<")
                return html_content
        except Exception:
            return html_content

    async def get_page_html(
        self, format_html: bool = True, max_length: int = 550000
    ) -> Dict[str, Any]:
        try:
            tab = self.get_current_tab()
            html_content = await tab.page.evaluate(
                """
                () => {
                    const body = document.body;
                    if (!body) {
                        return '<body></body>';
                    }
                    
                    const clonedBody = body.cloneNode(true);
                    
                    const unnecessarySelectors = [
                        'script',
                        'style',
                        'noscript',
                        'link[rel="stylesheet"]',
                        'link[rel="icon"]',
                        'link[rel="prefetch"]',
                        'link[rel="preload"]',
                        'meta',
                        'base',
                        'template',
                        'script[type="application/ld+json"]',
                        'script[type="text/template"]'
                    ];
                    
                    unnecessarySelectors.forEach(selector => {
                        const elements = clonedBody.querySelectorAll(selector);
                        elements.forEach(el => el.remove());
                    });
                    
                    const iframes = clonedBody.querySelectorAll('iframe');
                    Array.from(iframes).forEach((iframe, index) => {
                        const marker = document.createElement('div');
                        marker.className = 'iframe-placeholder';
                        marker.setAttribute('data-iframe-index', index.toString());
                        marker.setAttribute('data-iframe-src', iframe.src || 'about:blank');
                        marker.setAttribute('data-iframe-id', iframe.id || '');
                        marker.setAttribute('data-iframe-name', iframe.name || '');
                        marker.textContent = `[IFRAME #${index}: ${iframe.src || 'about:blank'}]`;
                        
                        ['id', 'class', 'name', 'title', 'data-*'].forEach(attr => {
                            if (attr === 'data-*') {
                                for (let i = 0; i < iframe.attributes.length; i++) {
                                    const attrName = iframe.attributes[i].name;
                                    if (attrName.startsWith('data-')) {
                                        marker.setAttribute(attrName, iframe.attributes[i].value);
                                    }
                                }
                            } else if (iframe.hasAttribute(attr)) {
                                marker.setAttribute(attr, iframe.getAttribute(attr));
                            }
                        });
                        
                        iframe.parentNode.replaceChild(marker, iframe);
                    });
                    
                    function cleanupTextNodes(node) {
                        for (let i = node.childNodes.length - 1; i >= 0; i--) {
                            const child = node.childNodes[i];
                            if (child.nodeType === Node.TEXT_NODE) {
                                if (child.textContent.trim() === '' && 
                                    (child.previousSibling?.nodeType === Node.ELEMENT_NODE || 
                                     child.nextSibling?.nodeType === Node.ELEMENT_NODE)) {
                                    node.removeChild(child);
                                }
                            } else if (child.nodeType === Node.ELEMENT_NODE) {
                                cleanupTextNodes(child);
                            }
                        }
                    }
                    
                    cleanupTextNodes(clonedBody);
                    
                    return clonedBody.outerHTML;
                }
            """
            )

            if format_html and html_content:
                html_content = self._format_html(html_content)

            original_length = len(html_content)
            truncated = False

            if len(html_content) > max_length:
                html_content = html_content[:max_length]
                truncated = True

            return self.success_response(
                data={
                    "html": html_content,
                    "original_length": original_length,
                    "truncated": truncated,
                    "shown_length": len(html_content),
                },
                message=f"HTML extracted (length: {original_length:,} chars)",
            )

        except Exception as e:
            return await self.handle_error(e, "get_page_html")

    async def evaluate_javascript(
        self, function: str, element_ref: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        try:
            tab = self.get_current_tab()

            if element_ref and element_ref.get("ref") and element_ref.get("element"):
                snapshot = tab.snapshot_or_die()
                locator = snapshot.ref_locator(element_ref)
                if not locator:
                    return await self.handle_error(
                        ValueError(f"Element not found: {element_ref}"),
                        "evaluate_javascript",
                    )

                result = await locator.evaluate(function)
            else:
                result = await tab.page.evaluate(function)

            return self.success_response(
                {"result": result}, "JavaScript evaluated successfully"
            )
        except Exception as e:
            return await self.handle_error(e, "evaluate_javascript")
