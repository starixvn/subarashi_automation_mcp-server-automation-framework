from .base_service import BaseService, ServiceResult


class KeyboardService(BaseService):
    def __init__(self, context):
        super().__init__(context)

    async def press_key(self, key: str) -> ServiceResult:
        try:
            tab = self.context.current_tab_or_die()

            await tab.page.keyboard.press(key)

            return ServiceResult(
                success=True, message=f"Pressed key '{key}'", data={"key": key}
            )
        except Exception as e:
            return ServiceResult(
                success=False,
                message=f"Failed to press key '{key}': {str(e)}",
                error=str(e),
            )
