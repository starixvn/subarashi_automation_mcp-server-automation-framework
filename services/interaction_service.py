from typing import Dict, Any, Optional, List
from .base_service import BaseService, ServiceResult


class InteractionService(BaseService):
    def __init__(self, context):
        super().__init__(context)

    async def click_element(self, element_ref: Dict[str, Any]) -> ServiceResult:
        try:
            tab = self.context.current_tab_or_die()
            snapshot = tab.snapshot_or_die()

            locator = snapshot.ref_locator(element_ref)
            await locator.click()

            return ServiceResult(
                success=True,
                message=f"Clicked {element_ref['element']}",
                data={"element": element_ref["element"]},
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
    ) -> ServiceResult:
        try:
            tab = self.context.current_tab_or_die()
            snapshot = tab.snapshot_or_die()

            locator = snapshot.ref_locator(element_ref)

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
            tab = self.context.current_tab_or_die()
            snapshot = tab.snapshot_or_die()

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
        self, element_ref: Dict[str, Any], values: List[str]
    ) -> ServiceResult:
        try:
            tab = self.context.current_tab_or_die()
            snapshot = tab.snapshot_or_die()

            locator = snapshot.ref_locator(element_ref)
            await locator.select_option(values)

            return ServiceResult(
                success=True,
                message=f"Selected {values} in {element_ref['element']}",
                data={"element": element_ref["element"], "values": values},
            )
        except Exception as e:
            return ServiceResult(
                success=False,
                message=f"Failed to select option in {element_ref['element']}: {str(e)}",
                error=str(e),
            )

    async def get_text_content(self, selector: str) -> ServiceResult:
        try:
            tab = self.context.current_tab_or_die()
            text = await tab.page.text_content(selector)

            return ServiceResult(
                success=True,
                message=f"Retrieved text content from {selector}",
                data={"selector": selector, "text": text or "(empty)"},
            )
        except Exception as e:
            return ServiceResult(
                success=False,
                message=f"Failed to get text from {selector}: {str(e)}",
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
