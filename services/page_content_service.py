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
        self, format_html: bool = True, max_length: int = 150000
    ) -> Dict[str, Any]:
        try:
            tab = self.get_current_tab()
            html_content = await tab.page.evaluate("""
                () => {
                    const html = document.documentElement.outerHTML;
                    
                    const tempDiv = document.createElement('div');
                    tempDiv.innerHTML = html;
                    
                    const unnecessarySelectors = [
                        'head',
                        'script', 
                        'style',
                        'link[rel="stylesheet"]',
                        'link[rel="icon"]',
                        'meta',
                        'title',
                        'noscript'
                    ];
                    
                    unnecessarySelectors.forEach(selector => {
                        const elements = tempDiv.querySelectorAll(selector);
                        elements.forEach(el => el.remove());
                    });
                    
                    const iframes = tempDiv.querySelectorAll('iframe');
                    Array.from(iframes).forEach((iframe, index) => {
                        try {
                            const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
                            if (iframeDoc) {
                                const iframeBody = iframeDoc.body;
                                if (iframeBody) {
                                    const comment = document.createComment(
                                        ` IFRAME #${index} CONTENT: ${iframeBody.innerHTML.substring(0, 500)} `
                                    );
                                    iframe.parentNode.insertBefore(comment, iframe.nextSibling);
                                }
                            } else {
                                const comment = document.createComment(
                                    ` IFRAME #${index} (cross-origin): src="${iframe.src}" `
                                );
                                iframe.parentNode.insertBefore(comment, iframe.nextSibling);
                            }
                        } catch (e) {
                            const comment = document.createComment(
                                ` IFRAME #${index} (access denied): src="${iframe.src}" `
                            );
                            iframe.parentNode.insertBefore(comment, iframe.nextSibling);
                        }
                    });
                    
                    const body = tempDiv.querySelector('body');
                    if (body) {
                        return body.outerHTML;
                    }
                    
                    return tempDiv.innerHTML;
                }
            """)

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
