from typing import List, Dict, Any


class QueryProcessor:
    """Processes queries and handles tool calls."""
    
    def __init__(self, session_manager, anthropic_service):
        """Initialize the query processor.
        
        Args:
            session_manager: The SessionManager instance
            anthropic_service: The AnthropicService instance
        """
        self.session_manager = session_manager
        self.anthropic_service = anthropic_service
        
    async def process_query(self, query: str) -> str:
        """Process a query using Claude and available tools.
        
        Args:
            query: The user's query
            
        Returns:
            The final response text
        """
        messages = [{"role": "user", "content": query}]
        
        # Get available tools
        tools = await self.session_manager.list_tools()
        available_tools = [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema,
            }
            for tool in tools
        ]
        
        # Initial Claude API call
        response = self.anthropic_service.generate_response(
            messages=messages,
            tools=available_tools,
        )
        
        # Process response and handle tool calls
        tool_results = []
        final_text = []
        
        for content in response.content:
            if content.type == "text":
                final_text.append(content.text)
            elif content.type == "tool_use":
                tool_name = content.name
                tool_args = content.input
                
                # Execute tool call
                result = await self.session_manager.call_tool(tool_name, tool_args)
                tool_results.append({"call": tool_name, "result": result})
                final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")
                
                # Continue conversation with tool results
                if hasattr(content, "text") and content.text:
                    messages.append({"role": "assistant", "content": content.text})
                messages.append({"role": "user", "content": result.content})
                
                # Get next response from Claude
                response = self.anthropic_service.generate_response(
                    messages=messages,
                )
                
                final_text.append(response.content[0].text)
                
        return "\n".join(final_text) 