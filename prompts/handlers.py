import logging
from typing import Dict, List, Optional, Any, Callable
from mcp.types import Prompt as MCPPrompt, GetPromptResult
from mcp.server.fastmcp.prompts.base import Message

from .registry import get_default_prompts, get_prompt_by_name

logger = logging.getLogger(__name__)


def get_prompts_handlers() -> Dict[str, Callable]:
    async def list_prompts() -> List[MCPPrompt]:
        try:
            prompts = get_default_prompts()
            mcp_prompts = []
            for prompt in prompts:
                mcp_prompt = MCPPrompt(
                    name=prompt.name, description=prompt.description, arguments=[]
                )
                mcp_prompts.append(mcp_prompt)

            logger.debug(f"Listed {len(mcp_prompts)} FastMCP prompts")
            return mcp_prompts

        except Exception as e:
            logger.error(f"Error listing prompts: {e}")
            return []

    async def get_prompt(
        name: str, arguments: Optional[Dict[str, Any]] = None
    ) -> GetPromptResult:
        try:
            prompt = get_prompt_by_name(name)
            if not prompt:
                raise ValueError(f"Prompt '{name}' not found")

            messages = await prompt.render(arguments or {})

            mcp_messages = []
            for msg in messages:
                mcp_msg = Message(role=msg.role, content=msg.content)
                mcp_messages.append(mcp_msg)

            result = GetPromptResult(
                description=prompt.description or "", messages=mcp_messages
            )

            logger.debug(
                f"Rendered FastMCP prompt '{name}' with {len(mcp_messages)} messages"
            )
            return result

        except Exception as e:
            logger.error(f"Error getting prompt '{name}': {e}")
            return GetPromptResult(description=f"Error: {str(e)}", messages=[])

    return {"list_prompts": list_prompts, "get_prompt": get_prompt}
