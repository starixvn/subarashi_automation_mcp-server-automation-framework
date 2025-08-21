from typing import Dict, Any, Optional, List
from .base_service import BaseService, ServiceResult
from services.vision_service import VisionService
from core.snapshot import PageSnapshot


class InteractionService(BaseService):
    def __init__(self, context):
        super().__init__(context)

    async def click_element(
        self,
        element_ref: Dict[str, Any],
        modifiers: Optional[List[str]] = None,
        click_type: str = "left",
        click_count: int = 1,
        button_delay: int = 0,
    ) -> ServiceResult:
        try:
            tab = self.get_current_tab()
            page = tab.page
            snapshot = PageSnapshot(page)
            await snapshot.snapshot_for_ai()

            locator = snapshot.ref_locator(element_ref)

            click_options = {}
            if modifiers:
                click_options["modifiers"] = modifiers
            if click_type != "left":
                click_options["button"] = click_type
            if click_count != 1:
                click_options["click_count"] = click_count
            if button_delay > 0:
                click_options["delay"] = button_delay

            await locator.click(**click_options)

            return ServiceResult(
                success=True,
                message=f"Clicked {element_ref.get('element', element_ref.get('ref', 'element'))}",
                data={
                    "element": element_ref.get(
                        "element", element_ref.get("ref", "element")
                    )
                },
            )
        except Exception as e:
            return ServiceResult(
                success=False,
                message=f"Failed to click {element_ref['element']}: {str(e)}",
                error=str(e),
            )

    async def type_text(
        self,
        element_ref: Dict[str, Any],
        text: str,
        slowly: bool = False,
        submit: bool = False,
        clear_first: bool = True,
    ) -> ServiceResult:
        try:
            tab = self.get_current_tab()
            page = tab.page

            snapshot = PageSnapshot(page)

            await snapshot.snapshot_for_ai()

            locator = snapshot.ref_locator(element_ref)

            if clear_first:
                await locator.clear()

            if slowly:
                await locator.press_sequentially(text)
            else:
                await locator.fill(text)

            if submit:
                await locator.press("Enter")

            action_type = "typed sequentially" if slowly else "filled"
            submit_text = " and submitted" if submit else ""

            return ServiceResult(
                success=True,
                message=f"Successfully {action_type} text into {element_ref['element']}{submit_text}",
                data={
                    "element": element_ref["element"],
                    "text": text,
                    "slowly": slowly,
                    "submitted": submit,
                },
            )
        except Exception as e:
            return ServiceResult(
                success=False,
                message=f"Failed to type into {element_ref['element']}: {str(e)}",
                error=str(e),
            )

    async def hover_element(self, element_ref: Dict[str, Any]) -> ServiceResult:
        try:
            tab = self.get_current_tab()
            page = tab.page

            snapshot = PageSnapshot(page)

            await snapshot.snapshot_for_ai()

            locator = snapshot.ref_locator(element_ref)
            await locator.hover()

            return ServiceResult(
                success=True,
                message=f"Hovered over {element_ref['element']}",
                data={"element": element_ref["element"]},
            )
        except Exception as e:
            return ServiceResult(
                success=False,
                message=f"Failed to hover over {element_ref['element']}: {str(e)}",
                error=str(e),
            )

    async def select_option(
        self, element_ref: Dict[str, Any], option: str
    ) -> ServiceResult:
        try:
            tab = self.get_current_tab()
            page = tab.page
            snapshot = PageSnapshot(page)
            await snapshot.snapshot_for_ai()
            locator = snapshot.ref_locator(element_ref)
            await locator.select_option(option)

            return ServiceResult(
                success=True,
                message=f"Selected {option} in {element_ref['element']}",
                data={"element": element_ref["element"], "option": option},
            )
        except Exception as e:
            return ServiceResult(
                success=False,
                message=f"Failed to select option in {element_ref['element']}: {str(e)}",
                error=str(e),
            )

    async def get_text_content(self, element_ref: Dict[str, Any]) -> ServiceResult:
        try:
            tab = self.context.current_tab_or_die()
            snapshot = tab.snapshot_or_die()

            locator = snapshot.ref_locator(element_ref)
            text = await locator.inner_text()

            if text:
                text = text.replace("\t", " ")
                text = " ".join(text.split())

            return ServiceResult(
                success=True,
                message=f"Retrieved text content from {element_ref['element']}",
                data={"element": element_ref["element"], "text": text or "(empty)"},
            )
        except Exception as e:
            return ServiceResult(
                success=False,
                message=f"Failed to get text from {element_ref['element']}: {str(e)}",
                error=str(e),
            )

    async def get_contents(
        self,
        selector: Optional[str] = None,
        element_ref: Optional[Any] = None,
        preserve_formatting: bool = True,
        normalize_whitespace: bool = True,
        include_screenshot: bool = False,
        screenshot_quality: int = 80,
    ) -> ServiceResult:
        try:
            tab = self.context.current_tab_or_die()

            if element_ref:
                snapshot = tab.snapshot_or_die()

                if hasattr(element_ref, "element") and hasattr(element_ref, "ref"):
                    ref_dict = {"element": element_ref.element, "ref": element_ref.ref}
                    element_description = element_ref.element
                else:
                    ref_dict = element_ref
                    element_description = element_ref.get("element", "element")

                locator = snapshot.ref_locator(ref_dict)
            elif selector:
                locator = tab.page.locator(selector)
                element_description = selector
            else:
                return ServiceResult(
                    success=False,
                    message="Either selector or element_ref must be provided",
                    error="No selection method provided",
                )

            text_method = "innerText" if preserve_formatting else "textContent"

            text = await locator.evaluate(
                f"""
                (element) => {{
                    if (!element) return null;
                    
                    let text = element.{text_method} || '';
                    
                    if ({str(normalize_whitespace).lower()}) {{
                        if ({str(preserve_formatting).lower()}) {{
                            text = text.replace(/[ \\t]+/g, ' ').trim();
                            text = text.replace(/\\n\\s*\\n/g, '\\n');
                        }} else {{
                            text = text.replace(/\\s+/g, ' ').trim();
                            text = text.replace(/\\n\\s*\\n/g, '\\n');
                        }}
                    }}
                    
                    return text;
                }}
                """,
            )

            if text is None:
                return ServiceResult(
                    success=False,
                    message=f"Element not found: {element_description}",
                    error="Element not found",
                )

            result_data = {
                "selector": selector,
                "text": text or "(empty)",
                "method": text_method,
                "preserve_formatting": preserve_formatting,
                "normalize_whitespace": normalize_whitespace,
                "text_length": len(text) if text else 0,
            }

            if include_screenshot and text:
                try:
                    vision_service = VisionService(self.context)
                    screenshot_result = await vision_service.take_screenshot(
                        element_selector=selector,
                        quality=screenshot_quality,
                        format="png",
                    )

                    if screenshot_result.success and screenshot_result.data:
                        content = screenshot_result.data.get("content", [])
                        if content and len(content) > 0 and "data" in content[0]:
                            result_data["screenshot"] = content[0]["data"]
                            result_data["has_screenshot"] = True
                        else:
                            result_data["has_screenshot"] = False
                            result_data["screenshot_error"] = (
                                "No screenshot data in response"
                            )
                    else:
                        result_data["has_screenshot"] = False
                        result_data["screenshot_error"] = (
                            screenshot_result.message
                            if not screenshot_result.success
                            else "No screenshot data"
                        )
                except ImportError:
                    result_data["has_screenshot"] = False
                    result_data["screenshot_error"] = "VisionService not available"
                except Exception as e:
                    result_data["has_screenshot"] = False
                    result_data["screenshot_error"] = str(e)
            else:
                result_data["has_screenshot"] = False

            success_message = f"Retrieved contents from {selector} using {text_method}"
            if include_screenshot:
                success_message += f" with screenshot ({'included' if result_data.get('has_screenshot') else 'failed'})"

            return ServiceResult(
                success=True,
                message=success_message,
                data=result_data,
            )
        except Exception as e:
            return ServiceResult(
                success=False,
                message=f"Failed to get contents from {selector}: {str(e)}",
                error=str(e),
            )

    async def drag_element(
        self, start_ref: Dict[str, Any], end_ref: Dict[str, Any]
    ) -> ServiceResult:
        try:
            tab = self.context.current_tab_or_die()
            snapshot = tab.snapshot_or_die()

            start_locator = snapshot.ref_locator(start_ref)
            end_locator = snapshot.ref_locator(end_ref)

            await start_locator.drag_to(end_locator)

            return ServiceResult(
                success=True,
                message=f"Dragged from {start_ref['element']} to {end_ref['element']}",
                data={
                    "start_element": start_ref["element"],
                    "end_element": end_ref["element"],
                },
            )
        except Exception as e:
            return ServiceResult(
                success=False, message=f"Failed to drag: {str(e)}", error=str(e)
            )
