from typing import Dict, Any, Optional
from .base_service import BaseService, ServiceResult


class DialogsService(BaseService):
    def __init__(self, context):
        super().__init__(context)

    async def handle_dialog(
        self, accept: bool, prompt_text: Optional[str] = None
    ) -> ServiceResult:
        try:
            dialog_state = None
            for state in self.context.modal_states():
                if state.type.value == "dialog":
                    dialog_state = state
                    break

            if not dialog_state:
                return ServiceResult(
                    success=False,
                    message="No dialog visible",
                    error="No dialog modal state found",
                )

            if accept:
                await dialog_state.dialog.accept(prompt_text or "")
                action = "accepted"
            else:
                await dialog_state.dialog.dismiss()
                action = "dismissed"

            self.context.clear_modal_state(dialog_state)

            return ServiceResult(
                success=True,
                message=f"Dialog {action}",
                data={
                    "action": action,
                    "dialog_type": dialog_state.dialog.type,
                    "prompt_text": prompt_text if accept and prompt_text else None,
                },
            )
        except Exception as e:
            return ServiceResult(
                success=False,
                message=f"Failed to handle dialog: {str(e)}",
                error=str(e),
            )
