from mcp.server.fastmcp import FastMCP, Context
from context import ServerContext
from services import PageContentService
from services import CoreService


def register_content_tools(app: FastMCP, server_context: ServerContext) -> None:
    @app.tool()
    async def browser_get_page_text(context: Context) -> str:
        try:
            tab = server_context.current_tab_or_die()
            page = tab.page

            main_text = await page.evaluate(
                "() => document.body.innerText || document.body.textContent || ''"
            )
            all_text = main_text

            frames = page.frames
            for i, frame in enumerate(frames):
                try:
                    if frame == page.main_frame:
                        continue

                    frame_text = await frame.evaluate(
                        "() => document.body ? (document.body.innerText || document.body.textContent || '') : ''"
                    )

                    if frame_text and frame_text.strip():
                        frame_name = frame.name or f"frame_{i}"
                        frame_url = frame.url or "about:blank"

                        all_text += f"\n\n--- FRAME '{frame_name}' CONTENT ---"
                        all_text += f"\nFrame URL: {frame_url}"
                        all_text += f"\n{frame_text}"
                        all_text += f"\n--- END FRAME '{frame_name}' ---"

                except Exception as e:
                    frame_name = frame.name or f"frame_{i}"
                    all_text += f"\n\n--- FRAME '{frame_name}' (Access Restricted) ---"
                    all_text += f"\nError: {str(e)}"
                    all_text += f"\n--- END FRAME '{frame_name}' ---"

            try:
                iframe_elements = await page.query_selector_all("iframe")
                for i, iframe in enumerate(iframe_elements):
                    try:
                        src = await iframe.get_attribute("src") or "about:blank"
                        name = await iframe.get_attribute("name") or f"iframe_{i + 1}"

                        frame = None
                        for f in frames:
                            try:
                                if f.name == name or f.url == src:
                                    frame = f
                                    break
                            except Exception:
                                continue

                        if frame and frame != page.main_frame:
                            frame_text = await frame.evaluate(
                                "() => document.body ? (document.body.innerText || document.body.textContent || '') : ''"
                            )
                            if (
                                frame_text
                                and frame_text.strip()
                                and f"FRAME '{name}'" not in all_text
                            ):
                                all_text += f"\n\n--- IFRAME '{name}' CONTENT ---"
                                all_text += f"\nIframe src: {src}"
                                all_text += f"\n{frame_text}"
                                all_text += f"\n--- END IFRAME '{name}' ---"
                    except Exception as e:
                        name = await iframe.get_attribute("name") or f"iframe_{i + 1}"
                        if f"IFRAME '{name}'" not in all_text:
                            all_text += f"\n\n--- IFRAME '{name}' (Access Error) ---"
                            all_text += f"\nError: {str(e)}"
                            all_text += f"\n--- END IFRAME '{name}' ---"
            except Exception:
                pass

            core_service = CoreService(server_context)
            url_result = await core_service.get_current_url()
            title_result = await core_service.get_page_title()

            current_url = (
                url_result["data"]["url"] if url_result["success"] else "Unknown"
            )
            page_title = (
                title_result["data"]["title"] if title_result["success"] else "Unknown"
            )
            text_length = len(all_text)

            return f"Page Text Extracted:\n URL: {current_url}\n Title: {page_title}\n Text Length: {text_length:,} characters\n Status: Text extraction completed\n\n{all_text}"

        except Exception as e:
            return f"Failed to get page text: {str(e)}"

    @app.tool()
    async def browser_get_page_html(context: Context) -> str:
        service = PageContentService(server_context)
        result = await service.get_page_html()
        if not result["success"]:
            return f"Failed to get page HTML: {result['error']}"

        core_service = CoreService(server_context)
        url_result = await core_service.get_current_url()
        title_result = await core_service.get_page_title()

        current_url = url_result["data"]["url"] if url_result["success"] else "Unknown"
        page_title = (
            title_result["data"]["title"] if title_result["success"] else "Unknown"
        )
        html_content = result["data"]["html"]
        html_length = len(html_content)
        truncated = result["data"].get("truncated", False)

        status_info = f"HTML Length: {html_length:,} characters"
        if truncated:
            original_length = result["data"].get("original_length", html_length)
            status_info += f" (truncated from {original_length:,})"

        return f"Page HTML Extracted:\n URL: {current_url}\n Title: {page_title}\n {status_info}\n Status: HTML extraction completed\n\n{html_content}"
