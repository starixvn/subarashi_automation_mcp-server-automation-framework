from typing import Dict, Any, List
from .base_service import BaseService, ServiceResult


class ConsoleService(BaseService):
    def __init__(self, context):
        super().__init__(context)

    async def clear_console(self) -> ServiceResult:
        try:
            tab = self.context.current_tab_or_die()

            tab.clear_console_messages()

            return ServiceResult(
                success=True, message="Console messages cleared", data={"cleared": True}
            )
        except Exception as e:
            return ServiceResult(
                success=False,
                message=f"Failed to clear console: {str(e)}",
                error=str(e),
            )

    async def get_console_messages(self) -> ServiceResult:
        try:
            tab = self.context.current_tab_or_die()

            messages = tab.get_console_messages()

            if not messages:
                return ServiceResult(
                    success=True,
                    message="No console messages",
                    data={"messages": [], "count": 0},
                )

            formatted_messages = []
            for msg in messages:
                formatted_messages.append(
                    {
                        "type": msg.get("type", "log"),
                        "text": msg.get("text", ""),
                        "timestamp": msg.get("timestamp"),
                    }
                )

            return ServiceResult(
                success=True,
                message=f"Retrieved {len(messages)} console messages",
                data={"messages": formatted_messages, "count": len(messages)},
            )
        except Exception as e:
            return ServiceResult(
                success=False,
                message=f"Failed to get console messages: {str(e)}",
                error=str(e),
            )
