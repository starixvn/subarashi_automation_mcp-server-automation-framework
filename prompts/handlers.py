"""
MCP Prompts Handlers

Handlers for MCP prompts protocol following low-level MCP server pattern.
"""

import logging
from typing import Dict, List, Optional, Any, Callable
from mcp.types import Prompt as MCPPrompt, GetPromptResult

from .registry import prompt_registry

logger = logging.getLogger(__name__)


def get_prompts_handlers() -> Dict[str, Callable]:
    """
    Get the MCP protocol handlers for prompts functionality.
    
    Returns:
        Dictionary of handler functions for MCP server integration
    """
    
    async def list_prompts() -> List[MCPPrompt]:
        """
        Handle prompts/list request.
        
        Returns list of all available prompts in MCP format.
        """
        try:
            prompts = prompt_registry.list_prompts()
            mcp_prompts = [prompt.to_mcp_prompt() for prompt in prompts]
            
            logger.debug(f"Listed {len(mcp_prompts)} prompts")
            return mcp_prompts
            
        except Exception as e:
            logger.error(f"Error listing prompts: {e}")
            return []
    
    async def get_prompt(name: str, arguments: Optional[Dict[str, Any]] = None) -> GetPromptResult:
        """
        Handle prompts/get request.
        
        Args:
            name: Name of the prompt to get
            arguments: Arguments for prompt rendering
            
        Returns:
            GetPromptResult with rendered prompt messages
        """
        try:
            # Get prompt from registry
            prompt = prompt_registry.get_prompt(name)
            if not prompt:
                raise ValueError(f"Prompt '{name}' not found")
            
            # Render prompt with arguments
            result = await prompt.render(arguments)
            
            logger.debug(f"Rendered prompt '{name}' with {len(result.messages)} messages")
            return result
            
        except Exception as e:
            logger.error(f"Error getting prompt '{name}': {e}")
            # Return empty result on error
            return GetPromptResult(
                description=f"Error: {str(e)}",
                messages=[]
            )
    
    return {
        "list_prompts": list_prompts,
        "get_prompt": get_prompt
    } 