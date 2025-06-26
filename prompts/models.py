"""
MCP Prompts Models

Models for MCP prompt system following the exact MCP protocol specification.
"""

from typing import List, Optional, Dict, Any, Callable, Awaitable, Union
from pydantic import BaseModel, Field
from mcp.types import (
    Prompt as MCPPrompt,
    PromptArgument as MCPPromptArgument, 
    PromptMessage as MCPPromptMessage,
    GetPromptResult,
    Content,
    TextContent,
    Role
)

class PromptArgument(BaseModel):
    """MCP Prompt Argument following protocol specification."""
    
    name: str
    """The name of the argument."""
    
    description: Optional[str] = None
    """A human-readable description of the argument."""
    
    required: Optional[bool] = None
    """Whether this argument must be provided."""
    
    def to_mcp_argument(self) -> MCPPromptArgument:
        """Convert to MCP protocol format."""
        return MCPPromptArgument(
            name=self.name,
            description=self.description,
            required=self.required
        )


class PromptMessage(BaseModel):
    """MCP Prompt Message following protocol specification."""
    
    role: Role
    """Message role: 'user' or 'assistant'."""
    
    content: Content
    """Message content (text, image, etc.)."""
    
    def to_mcp_message(self) -> MCPPromptMessage:
        """Convert to MCP protocol format."""
        return MCPPromptMessage(
            role=self.role,
            content=self.content
        )


# Type for prompt generator functions
PromptGenerator = Callable[[Dict[str, Any]], Awaitable[List[PromptMessage]]]


class Prompt(BaseModel):
    """MCP Prompt following protocol specification."""
    
    name: str
    """The name of the prompt or prompt template."""
    
    description: Optional[str] = None
    """An optional description of what this prompt provides."""
    
    arguments: Optional[List[PromptArgument]] = None
    """A list of arguments to use for templating the prompt."""
    
    generator: Optional[PromptGenerator] = Field(None, exclude=True)
    """Function to generate prompt messages (not serialized)."""
    
    def to_mcp_prompt(self) -> MCPPrompt:
        """Convert to MCP protocol format."""
        mcp_arguments = None
        if self.arguments:
            mcp_arguments = [arg.to_mcp_argument() for arg in self.arguments]
            
        return MCPPrompt(
            name=self.name,
            description=self.description,
            arguments=mcp_arguments
        )
    
    async def render(self, arguments: Optional[Dict[str, Any]] = None) -> GetPromptResult:
        """Render the prompt with arguments to get the final result."""
        if not self.generator:
            # Static prompt without generator
            return GetPromptResult(
                description=self.description,
                messages=[]
            )
        
        # Validate required arguments
        if self.arguments:
            required_args = {arg.name for arg in self.arguments if arg.required}
            provided_args = set(arguments.keys()) if arguments else set()
            missing_args = required_args - provided_args
            
            if missing_args:
                raise ValueError(f"Missing required arguments: {', '.join(missing_args)}")
        
        # Generate messages using the generator function
        messages = await self.generator(arguments or {})
        
        # Convert to MCP format
        mcp_messages = [msg.to_mcp_message() for msg in messages]
        
        return GetPromptResult(
            description=self.description,
            messages=mcp_messages
        )


def create_text_message(role: Role, text: str) -> PromptMessage:
    """Helper to create a text message."""
    return PromptMessage(
        role=role,
        content=TextContent(type="text", text=text)
    )


def create_user_message(text: str) -> PromptMessage:
    """Helper to create a user message."""
    return create_text_message("user", text)


def create_assistant_message(text: str) -> PromptMessage:
    """Helper to create an assistant message.""" 
    return create_text_message("assistant", text) 