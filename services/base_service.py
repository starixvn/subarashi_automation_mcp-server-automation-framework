from abc import ABC
from typing import TYPE_CHECKING, Any, Dict, Optional, List
from dataclasses import dataclass
import logging

if TYPE_CHECKING:
    from ..context import ServerContext

logger = logging.getLogger(__name__)


@dataclass
class ServiceResult:
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    def to_mcp_content(self) -> List[Dict[str, Any]]:
        if self.success:
            content = [{"type": "text", "text": self.message}]
            if self.data:
                content.append({"type": "text", "text": f"Data: {self.data}"})
            return content
        else:
            return [{"type": "text", "text": f"Error: {self.error or self.message}"}]


class BaseService(ABC):
    def __init__(self, context: "ServerContext"):
        self.context = context
        self.logger = logging.getLogger(self.__class__.__name__)

    def get_current_tab(self):
        return self.context.current_tab_or_die()

    async def ensure_tab(self):
        return await self.context.ensure_tab()

    def get_config(self):
        return self.context.config

    async def handle_error(self, error: Exception, operation: str) -> Dict[str, Any]:
        error_msg = f"Error in {operation}: {str(error)}"
        self.logger.error(error_msg)

        return {"success": False, "error": error_msg, "data": None}

    def success_response(self, data: Any = None, message: str = None) -> Dict[str, Any]:
        return {"success": True, "error": None, "data": data, "message": message}
