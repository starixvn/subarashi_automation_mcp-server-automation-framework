from mcp.server.fastmcp.prompts import Prompt
from mcp.server.fastmcp.prompts.base import UserMessage, AssistantMessage

__all__ = [
    "Prompt",
    "UserMessage",
    "AssistantMessage",
    "create_user_message",
    "create_assistant_message",
]


def create_user_message(text: str) -> UserMessage:
    return UserMessage(content=text)


def create_assistant_message(text: str) -> AssistantMessage:
    return AssistantMessage(content=text)
