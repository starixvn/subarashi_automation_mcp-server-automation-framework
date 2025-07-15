from typing import List, Optional, Dict, Any, Callable, Awaitable, Union
from pydantic import BaseModel, Field
from mcp.types import (
    Prompt as MCPPrompt,
    PromptArgument as MCPPromptArgument,
    PromptMessage as MCPPromptMessage,
    GetPromptResult,
    Content,
    TextContent,
    Role,
)


class PromptArgument(BaseModel):
    name: str

    description: Optional[str] = None

    required: Optional[bool] = None

    def to_mcp_argument(self) -> MCPPromptArgument:
        return MCPPromptArgument(
            name=self.name, description=self.description, required=self.required
        )


class PromptMessage(BaseModel):
    role: Role

    content: Content

    def to_mcp_message(self) -> MCPPromptMessage:
        return MCPPromptMessage(role=self.role, content=self.content)


PromptGenerator = Callable[[Dict[str, Any]], Awaitable[List[PromptMessage]]]


class Prompt(BaseModel):
    name: str

    description: Optional[str] = None

    arguments: Optional[List[PromptArgument]] = None

    generator: Optional[PromptGenerator] = Field(None, exclude=True)

    def to_mcp_prompt(self) -> MCPPrompt:
        mcp_arguments = None
        if self.arguments:
            mcp_arguments = [arg.to_mcp_argument() for arg in self.arguments]

        return MCPPrompt(
            name=self.name, description=self.description, arguments=mcp_arguments
        )

    async def render(
        self, arguments: Optional[Dict[str, Any]] = None
    ) -> GetPromptResult:
        if not self.generator:
            return GetPromptResult(description=self.description, messages=[])

        if self.arguments:
            required_args = {arg.name for arg in self.arguments if arg.required}
            provided_args = set(arguments.keys()) if arguments else set()
            missing_args = required_args - provided_args

            if missing_args:
                raise ValueError(
                    f"Missing required arguments: {', '.join(missing_args)}"
                )

        messages = await self.generator(arguments or {})

        mcp_messages = [msg.to_mcp_message() for msg in messages]

        return GetPromptResult(description=self.description, messages=mcp_messages)


def create_text_message(role: Role, text: str) -> PromptMessage:
    return PromptMessage(role=role, content=TextContent(type="text", text=text))


def create_user_message(text: str) -> PromptMessage:
    return create_text_message("user", text)


def create_assistant_message(text: str) -> PromptMessage:
    return create_text_message("assistant", text)
