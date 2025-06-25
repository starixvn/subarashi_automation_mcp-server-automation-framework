from typing import Dict, Any, TYPE_CHECKING
from .tool_schema import (
    define_tool_factory,
    ToolCapability,
    ToolType,
    ToolResult,
    ToolActionResult,
    Tool,
    ToolSchema,
)
from .schemas import GetPageHtmlInputSchema, GetPageContentInputSchema

if TYPE_CHECKING:
    from ..context import ServerContext
    from ..core.browser_context_factory import BrowserContextFactory


@define_tool_factory(
    capability=ToolCapability.CORE,
    name="browser_get_page_html",
    title="Get page HTML",
    description="Get optimized page HTML for element mapping - removes scripts/styles but keeps all interactive elements",
    input_schema=GetPageHtmlInputSchema,
    tool_type=ToolType.READ_ONLY,
)
def browser_get_page_html_factory(capture_snapshot: bool) -> Tool:
    def _format_html(html_content: str) -> str:
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            return soup.prettify()
        except ImportError:
            html_content = html_content.replace('><', '>\n<')
            return html_content
        except:
            return html_content

    async def handle(context: "ServerContext", params: Dict[str, Any]) -> ToolResult:
        validated_params = GetPageHtmlInputSchema(**params)
        
        tab = context.current_tab_or_die()
        
        code = ["// Get optimized page HTML for element mapping"]

        async def action() -> ToolActionResult:
            try:
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
                
                if validated_params.format_html and html_content:
                    html_content = _format_html(html_content)
                
                original_length = len(html_content)
                if len(html_content) > validated_params.max_length:
                    html_content = html_content[:validated_params.max_length] + "\n\n... (HTML truncated)"
                    info_msg = f"**Optimized HTML**: Removed scripts/styles | Original: {original_length:,} chars | Shown: {validated_params.max_length:,} chars (truncated)\n\n"
                else:
                    info_msg = f"**Optimized HTML**: Removed scripts/styles | Length: {original_length:,} characters\n\n"
                
                result_text = info_msg + "```html\n" + html_content + "\n```"
                
                return ToolActionResult(
                    content=[{
                        "type": "text",
                        "text": result_text,
                    }]
                )
                
            except Exception as e:
                return ToolActionResult(
                    content=[{
                        "type": "text", 
                        "text": f"**Error**: Failed to get page HTML: {str(e)}",
                    }]
                )

        return ToolResult(
            code=code,
            action=action,
            capture_snapshot=False,
            wait_for_network=False,
        )

    schema = ToolSchema(
        name="browser_get_page_html",
        title="Get page HTML",
        description="Get optimized page HTML for element mapping - removes unnecessary scripts/styles while preserving all interactive elements and their attributes",
        input_schema=GetPageHtmlInputSchema,
        tool_type=ToolType.READ_ONLY,
    )
    
    return Tool(
        capability=ToolCapability.CORE,
        schema=schema,
        handle=handle
    )


@define_tool_factory(
    capability=ToolCapability.CORE,
    name="browser_get_page_content",
    title="Get page content",
    description="Get structured page content including text, links, and metadata",
    input_schema=GetPageContentInputSchema,
    tool_type=ToolType.READ_ONLY,
)
def browser_get_page_content_factory(capture_snapshot: bool) -> Tool:
    async def handle(context: "ServerContext", params: Dict[str, Any]) -> ToolResult:
        validated_params = GetPageContentInputSchema(**params)
        
        tab = context.current_tab_or_die()
        
        code = ["// Extract structured page content for analysis"]

        async def action() -> ToolActionResult:
            try:    
                page_title = await tab.page.title()
                page_url = tab.page.url
                page_text = await tab.page.text_content('body') or ""
                
                if len(page_text) > validated_params.max_length:
                    page_text = page_text[:validated_params.max_length] + "... (truncated)"
                
                content_parts = [
                    f"**Page Title:** {page_title}",
                    f"**Page URL:** {page_url}",
                    "",
                    "**Page Text Content:**",
                    page_text
                ]
                
                if validated_params.include_meta:
                    try:
                        meta_data = await tab.page.evaluate("""
                            () => Array.from(document.querySelectorAll('meta')).map(m => ({
                                name: m.name || m.getAttribute('property'),
                                content: m.content
                            })).filter(m => m.name && m.content).slice(0, 20)
                        """)
                        
                        if meta_data:
                            content_parts.extend(["", "**Meta Tags:**"])
                            for meta in meta_data:
                                content_parts.append(f"- {meta['name']}: {meta['content']}")
                    except:
                        pass
                
                if validated_params.include_links:
                    try:
                        links = await tab.page.evaluate("""
                            () => Array.from(document.querySelectorAll('a[href]')).map(a => ({
                                href: a.href,
                                text: a.textContent.trim()
                            })).filter(l => l.text).slice(0, 30)
                        """)
                        
                        if links:
                            content_parts.extend(["", "**Links:**"])
                            for link in links:
                                content_parts.append(f"- [{link['text']}]({link['href']})")
                    except:
                        pass
                
                if validated_params.include_images:
                    try:
                        images = await tab.page.evaluate("""
                            () => Array.from(document.querySelectorAll('img[src]')).map(img => ({
                                src: img.src,
                                alt: img.alt || ''
                            })).slice(0, 20)
                        """)
                        
                        if images:
                            content_parts.extend(["", "**Images:**"])
                            for img in images:
                                alt_text = f" (alt: {img['alt']})" if img['alt'] else ""
                                content_parts.append(f"- {img['src']}{alt_text}")
                    except:
                        pass
                
                result_text = "\n".join(content_parts)
                
                return ToolActionResult(
                    content=[{
                        "type": "text",
                        "text": result_text,
                    }]
                )
                
            except Exception as e:
                return ToolActionResult(
                    content=[{
                        "type": "text",
                        "text": f"**Error**: Failed to get page content: {str(e)}",
                    }]
                )

        return ToolResult(
            code=code,
            action=action,
            capture_snapshot=False,
            wait_for_network=False,
        )

    schema = ToolSchema(
        name="browser_get_page_content",
        title="Get page content", 
        description="Get structured page content including text, links, and metadata",
        input_schema=GetPageContentInputSchema,
        tool_type=ToolType.READ_ONLY,
    )

    return Tool(capability=ToolCapability.CORE, schema=schema, handle=handle)


def _format_html_simple(html: str) -> str:
    try:
        import re
        html = re.sub(r'><', '>\n<', html)
        return html
    except:
        return html


# Export tools
def get_page_content_tools(capture_snapshot: bool = False) -> list[Tool]:
    return [
        browser_get_page_html_factory(capture_snapshot),
        browser_get_page_content_factory(capture_snapshot),
    ]


PAGE_CONTENT_TOOLS = get_page_content_tools(capture_snapshot=False) 