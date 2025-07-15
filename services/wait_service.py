from typing import Dict, Any, Optional
from .base_service import BaseService, ServiceResult


class WaitService(BaseService):
    def __init__(self, context):
        super().__init__(context)

    async def wait_for_timeout(self, seconds: float) -> ServiceResult:
        try:
            await self.context.wait_for_timeout(seconds)

            return ServiceResult(
                success=True,
                message=f"Waited for {seconds} seconds",
                data={"timeout": seconds},
            )
        except Exception as e:
            return ServiceResult(
                success=False,
                message=f"Failed to wait for timeout: {str(e)}",
                error=str(e),
            )

    async def wait_for_text(self, text: str) -> ServiceResult:
        try:
            tab = self.context.current_tab_or_die()

            await tab.page.wait_for_function(
                f"() => document.body.innerText.includes('{text}')"
            )

            return ServiceResult(
                success=True,
                message=f"Text '{text}' appeared on page",
                data={"text": text, "found": True},
            )
        except Exception as e:
            return ServiceResult(
                success=False,
                message=f"Failed to wait for text '{text}': {str(e)}",
                error=str(e),
            )

    async def wait_for_text_gone(self, text: str) -> ServiceResult:
        try:
            tab = self.context.current_tab_or_die()

            await tab.page.wait_for_function(
                f"() => !document.body.innerText.includes('{text}')"
            )

            return ServiceResult(
                success=True,
                message=f"Text '{text}' disappeared from page",
                data={"text": text, "gone": True},
            )
        except Exception as e:
            return ServiceResult(
                success=False,
                message=f"Failed to wait for text '{text}' to disappear: {str(e)}",
                error=str(e),
            )

    async def wait_for_selector(
        self, selector: str, timeout: float = 30.0
    ) -> ServiceResult:
        try:
            tab = self.context.current_tab_or_die()

            await tab.page.wait_for_selector(selector, timeout=int(timeout * 1000))

            return ServiceResult(
                success=True,
                message=f"Element '{selector}' appeared",
                data={"selector": selector, "timeout": timeout},
            )
        except Exception as e:
            return ServiceResult(
                success=False,
                message=f"Wait for selector '{selector}' failed: {str(e)}",
                error=str(e),
            )
