from typing import Dict, Any, Optional, TYPE_CHECKING
from .base_service import BaseService

if TYPE_CHECKING:
    from context import ServerContext

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

    async def get_page_content(
        self,
        include_meta: bool = False,
        include_links: bool = False,
        include_images: bool = False,
        max_length: int = 50000,
    ) -> Dict[str, Any]:
        try:
            tab = self.get_current_tab()
            page_title = await tab.page.title()
            page_url = tab.page.url
            page_text = await tab.page.text_content("body") or ""
            if len(page_text) > max_length:
                page_text = page_text[:max_length] + "... (truncated)"

            content_data = {
                "title": page_title,
                "url": page_url,
                "text": page_text,
                "text_length": len(page_text),
            }

            if include_meta:
                try:
                    meta_data = await tab.page.evaluate("""
                        () => Array.from(document.querySelectorAll('meta')).map(m => ({
                            name: m.name || m.getAttribute('property'),
                            content: m.content
                        })).filter(m => m.name && m.content).slice(0, 20)
                    """)
                    content_data["meta"] = meta_data
                except Exception:
                    content_data["meta"] = []

            if include_links:
                try:
                    links = await tab.page.evaluate("""
                        () => Array.from(document.querySelectorAll('a[href]')).map(a => ({
                            href: a.href,
                            text: a.textContent.trim()
                        })).filter(l => l.text).slice(0, 30)
                    """)
                    content_data["links"] = links
                except Exception:
                    content_data["links"] = []

            if include_images:
                try:
                    images = await tab.page.evaluate("""
                        () => Array.from(document.querySelectorAll('img[src]')).map(img => ({
                            src: img.src,
                            alt: img.alt || ''
                        })).slice(0, 20)
                    """)
                    content_data["images"] = images
                except Exception:
                    content_data["images"] = []

            return self.success_response(
                data=content_data, message=f"Page content extracted from {page_url}"
            )

        except Exception as e:
            return await self.handle_error(e, "get_page_content")

    async def get_page_text(self, selector: str = "body") -> Dict[str, Any]:
        try:
            tab = self.get_current_tab()
            text = await tab.page.text_content(selector) or ""

            return self.success_response(
                data={"text": text, "selector": selector},
                message=f"Text extracted from {selector}",
            )
        except Exception as e:
            return await self.handle_error(e, "get_page_text")

    async def search_text_in_page(self, search_text: str) -> Dict[str, Any]:
        try:
            tab = self.get_current_tab()
            found = await tab.page.evaluate(f"""
                () => {{
                    const text = '{search_text}';
                    const body = document.body;
                    const textContent = body.innerText || body.textContent;
                    
                    const index = textContent.toLowerCase().indexOf(text.toLowerCase());
                    if (index !== -1) {{
                        return {{
                            found: true,
                            index: index,
                            context: textContent.substring(Math.max(0, index - 50), index + text.length + 50)
                        }};
                    }}
                    return {{found: false}};
                }}
            """)

            return self.success_response(
                data=found, message=f"Search completed for '{search_text}'"
            )

        except Exception as e:
            return await self.handle_error(e, "search_text_in_page")
