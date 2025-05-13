import asyncio
import os
import sys
import json
from typing import Dict, Any, Optional, List
from contextlib import AsyncExitStack
import logging

from mcp import ClientSession
from mcp.client.sse import sse_client
from mcp.types import Tool, CallToolResult

from google import genai
from google.genai.types import Tool as GeminiTool
from google.genai.types import FunctionDeclaration, Content, Part
from google.genai.types import GenerateContentConfig

from dotenv import load_dotenv
from client.browser_delegate import ClientBrowserManager

load_dotenv()

logger = logging.getLogger(__name__)


class GeminiSSEClient:
    def __init__(self):
        """Initialize the Gemini SSE client."""
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self._session_context = None
        self._streams_context = None

        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")
        self.genai_client = genai.Client(api_key=gemini_api_key)
        self.function_declarations = []

        self.skip_tools = set()
        self.conversation_history = []

        # Add browser manager
        self.browser_manager = ClientBrowserManager()
        self.browser_initialized = False

        system_text = (
            "[SYSTEM INSTRUCTIONS - ALWAYS FOLLOW]\n"
            "You are a helpful AI assistant with access to various tools to assist users. "
            "When users request information or actions related to available tools, "
            "PROACTIVELY use appropriate tools to complete tasks without asking for further confirmation.\n\n"
            "INTELLIGENT WEB ANALYSIS:\n"
            "1. First, understand the user's goal (searching, clicking, reading content, etc.)\n"
            "2. Use Get-Page-HTML to get the full HTML structure of the current page\n"
            "3. Analyze the HTML structure to identify interactive elements (search boxes, buttons, forms)\n"
            "4. Look for semantic patterns in element attributes, not just fixed selectors\n"
            "5. Determine the most appropriate element for the task based on context\n\n"
            "STRATEGIC TOOL USAGE:\n"
            "1. Plan your approach before using tools - consider the most efficient sequence\n"
            "2. Use Browser-Find-By-XPath only after analyzing the page structure\n"
            "3. Try intuitive selectors based on the page's specific structure\n"
            "4. If an interaction fails, analyze the result and adjust your approach\n"
            "5. Use a single well-chosen tool action rather than multiple similar attempts\n\n"
            "ADAPTIVE ERROR HANDLING:\n"
            "1. If element selection fails, analyze why before trying alternatives\n"
            "2. Consider the website's design patterns and adjust your strategy\n"
            "3. Look for alternative paths to achieve the same goal\n"
            "4. Innovate solutions based on the specific website structure\n\n"
            "EFFECTIVE PROGRESS REPORTING:\n"
            "1. Explain your analysis process and reasoning\n"
            "2. Report tool usage and outcomes clearly\n"
            "3. If encountering difficulties, explain your adaptive strategy\n"
            "4. Summarize completed tasks and achievements\n\n"
            "GENERAL PRINCIPLES:\n"
            "1. Be proactive and autonomous - solve problems without asking for guidance\n"
            "2. Think strategically rather than trying multiple similar approaches\n"
            "3. Maintain conversation context and build on previous interactions\n"
            "4. Analyze each webpage uniquely rather than applying fixed patterns\n"
            "5. Prioritize effectiveness over number of tool calls\n\n"
            "Intelligently analyze each webpage and choose the most appropriate tools and approaches for each unique situation."
        )

        system_part = Part(text=system_text)

        initial_system_message = Content(role="user", parts=[system_part])
        self.conversation_history.append(initial_system_message)

    async def connect_to_sse_server(self, server_url: str):
        """Connect to an MCP server using SSE transport"""
        try:
            self._streams_context = sse_client(url=server_url)
            streams = await self._streams_context.__aenter__()

            self._session_context = ClientSession(*streams)
            self.session = await self._session_context.__aenter__()

            await self.session.initialize()

            response = await self.session.list_tools()
            tools = response.tools
            print("\nConnected to server with tools:", [tool.name for tool in tools])

            self.function_declarations = self.convert_mcp_tools_to_gemini_tools(tools)
            print(f"Converted {len(self.function_declarations)} tools for Gemini")

            if self.skip_tools:
                print(f"Skipped problematic tools: {self.skip_tools}")

            # Add custom message handler for browser commands
            if self.session:
                self.session.on_custom_message = self.handle_browser_command

        except Exception as e:
            print(f"Error connecting to server: {str(e)}")
            await self.cleanup()
            raise

    def convert_mcp_tools_to_gemini_tools(
        self, mcp_tools: List[Tool]
    ) -> List[GeminiTool]:
        """Convert MCP tools to Gemini tools format."""
        gemini_tools = []

        for tool in mcp_tools:
            try:
                if tool.name.startswith("API-") and tool.name in [
                    "API-OAuth2",
                    "API-Init",
                    "API-GET",
                    "API-POST",
                    "API-PUT",
                    "API-DELETE",
                    "API-BasicAuth",
                    "API-BearerToken",
                ]:
                    self.skip_tools.add(tool.name)
                    continue

                parameters = self.clean_schema(tool.inputSchema)

                function_declaration = FunctionDeclaration(
                    name=tool.name,
                    description=tool.description or f"Tool: {tool.name}",
                    parameters=parameters,
                )

                gemini_tool = GeminiTool(function_declarations=[function_declaration])
                gemini_tools.append(gemini_tool)

            except Exception as e:
                print(f"Error converting tool {tool.name}: {str(e)}")
                self.skip_tools.add(tool.name)

        return gemini_tools

    def clean_schema(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Clean MCP schema to be compatible with Gemini API."""
        if not isinstance(schema, dict):
            return {"type": "object"}

        clean_schema = schema.copy()

        if any(key in clean_schema for key in ["anyOf", "oneOf", "allOf"]):
            if "anyOf" in clean_schema:
                cleaned_items = []
                for item in clean_schema["anyOf"]:
                    cleaned_items.append(self.clean_schema(item))
                return {"anyOf": cleaned_items}
            elif "oneOf" in clean_schema:
                cleaned_items = []
                for item in clean_schema["oneOf"]:
                    cleaned_items.append(self.clean_schema(item))
                return {"oneOf": cleaned_items}
            elif "allOf" in clean_schema:
                cleaned_items = []
                for item in clean_schema["allOf"]:
                    cleaned_items.append(self.clean_schema(item))
                return {"allOf": cleaned_items}

        clean_schema.pop("title", None)
        clean_schema.pop("additionalProperties", None)

        if "type" not in clean_schema:
            clean_schema["type"] = "object"
        elif clean_schema["type"] not in [
            "string",
            "number",
            "integer",
            "boolean",
            "object",
            "array",
            "null",
        ]:
            clean_schema["type"] = "object"

        if "properties" in clean_schema and isinstance(
            clean_schema["properties"], dict
        ):
            properties = {}
            for key, value in list(clean_schema["properties"].items()):
                if value is True or value is False:
                    properties[key] = {
                        "type": "string",
                        "description": f"Property {key}",
                    }
                elif not isinstance(value, dict):
                    properties[key] = {
                        "type": "string",
                        "description": f"Property {key}",
                    }
                else:
                    if any(
                        special_key in value
                        for special_key in ["anyOf", "oneOf", "allOf"]
                    ):
                        properties[key] = {
                            "type": "string",
                            "description": f"Property {key} (simplified from complex schema)",
                        }
                    else:
                        clean_value = self.clean_schema(value)
                        properties[key] = clean_value

            clean_schema["properties"] = properties

        return clean_schema

    async def process_query(self, query: str) -> str:
        """Process a query using Gemini and MCP tools."""
        if not self.session:
            raise ValueError("Not connected to an MCP server")

        user_part = Part(text=query)
        user_prompt_content = Content(role="user", parts=[user_part])
        self.conversation_history.append(user_prompt_content)

        try:
            response = self.genai_client.models.generate_content(
                model="gemini-2.0-flash-001",
                contents=self.conversation_history,
                config=GenerateContentConfig(
                    temperature=0.2,
                    max_output_tokens=1000,
                    tools=self.function_declarations,
                ),
            )

            return await self.process_response(response)

        except Exception as e:
            return f"Error processing query: {str(e)}"

    async def process_response(self, response: Any) -> str:
        """Process Gemini response and handle tool calls properly."""
        final_text = []

        for candidate in response.candidates:
            if not candidate.content:
                continue

            assistant_content = candidate.content
            self.conversation_history.append(assistant_content)

            for part in assistant_content.parts:
                if hasattr(part, "text") and part.text:
                    final_text.append(part.text)

            tool_calls = []
            for part in assistant_content.parts:
                if hasattr(part, "function_call") and part.function_call is not None:
                    tool_calls.append(part.function_call)

            if not tool_calls:
                continue

            function_responses = []
            tool_results = []

            for function_call in tool_calls:
                tool_name = function_call.name
                tool_args = function_call.args

                call_info = f"[Calling tool: {tool_name} with arguments: {json.dumps(tool_args, indent=2)}]"
                print(call_info)
                tool_results.append(call_info)

                try:
                    if tool_name in self.skip_tools:
                        skip_msg = f"[Skipped problematic tool: {tool_name}]"
                        tool_results.append(skip_msg)
                        function_responses.append(
                            {
                                "name": tool_name,
                                "response": {
                                    "error": f"Tool {tool_name} is not supported"
                                },
                            }
                        )
                        continue

                    result = await self.session.call_tool(
                        name=tool_name, arguments=tool_args
                    )
                    tool_result_text = self.extract_text_from_tool_result(result)
                    tool_results.append(f"[Tool result: {tool_result_text}]")

                    function_responses.append(
                        {"name": tool_name, "response": {"result": tool_result_text}}
                    )

                except Exception as e:
                    error_msg = f"Error calling tool {tool_name}: {str(e)}"
                    print(error_msg)
                    tool_results.append(error_msg)

                    function_responses.append(
                        {"name": tool_name, "response": {"error": str(e)}}
                    )

            if len(function_responses) != len(tool_calls):
                print(
                    f"WARNING: Number of function responses ({len(function_responses)}) does not match number of tool calls ({len(tool_calls)})"
                )
                while len(function_responses) < len(tool_calls):
                    function_responses.append(
                        {
                            "name": "dummy_tool",
                            "response": {
                                "error": "Placeholder response to ensure matching count"
                            },
                        }
                    )

            final_text.extend(tool_results)

            function_response_parts = []
            for response_data in function_responses:
                if "result" in response_data["response"]:
                    function_response_part = Part(
                        function_response={
                            "name": response_data["name"],
                            "response": {"result": response_data["response"]["result"]},
                        }
                    )
                else:
                    function_response_part = Part(
                        function_response={
                            "name": response_data["name"],
                            "response": {
                                "error": response_data["response"].get(
                                    "error", "Unknown error"
                                )
                            },
                        }
                    )
                function_response_parts.append(function_response_part)

            if function_response_parts:
                function_response_content = Content(
                    role="function", parts=function_response_parts
                )

                self.conversation_history.append(function_response_content)

                try:
                    follow_up_response = self.genai_client.models.generate_content(
                        model="gemini-2.0-flash-001",
                        contents=self.conversation_history,
                        config=GenerateContentConfig(
                            temperature=0.2,
                            max_output_tokens=1000,
                            tools=self.function_declarations,
                        ),
                    )

                    follow_up_text = await self.process_response(follow_up_response)
                    if follow_up_text:
                        final_text.append(follow_up_text)
                except Exception as e:
                    error_msg = f"Error in follow-up response: {str(e)}"
                    print(error_msg)
                    final_text.append(error_msg)

        return "\n".join([text for text in final_text if text])

    def extract_text_from_tool_result(self, result: CallToolResult) -> str:
        """Extract text content from MCP tool result."""
        if result.isError:
            return f"Error: {' '.join([c.text for c in result.content if hasattr(c, 'text')])}"

        text_parts = []
        for content in result.content:
            if hasattr(content, "text") and content.text:
                text_parts.append(content.text)

        return "\n".join(text_parts) if text_parts else "No text result"

    async def chat_loop(self):
        """Run an interactive chat loop."""
        print("\nGemini MCP Client Started!")
        print("Type your queries or 'exit' to quit.")

        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() in ["exit", "quit"]:
                    print("Exiting chat...")
                    break

                response = await self.process_query(query)
                print(f"\nAssistant: {response}")

            except Exception as e:
                print(f"\nError in chat loop: {str(e)}")

    async def handle_browser_command(self, message):
        """Handle browser commands from server."""
        if message.get("type") != "browser_command":
            return

        command = message.get("command")
        command_id = message.get("command_id")

        logger.info(f"Received browser command: {command}")

        if not self.browser_initialized:
            await self.browser_manager.initialize()
            self.browser_initialized = True

        result = await self.browser_manager.execute_command(command)

        # Send result back to server
        await self.session.send_custom_message(
            {"type": "browser_result", "command_id": command_id, "result": result}
        )

    async def cleanup(self):
        """Properly clean up all resources."""
        try:
            if self._session_context:
                await self._session_context.__aexit__(None, None, None)

            if self._streams_context:
                await self._streams_context.__aexit__(None, None, None)

            # Add browser cleanup
            if self.browser_initialized:
                await self.browser_manager.close()

        except Exception as e:
            print(f"Error during cleanup: {str(e)}")


async def main():
    if len(sys.argv) < 2:
        print(
            "Usage: python client_sse_gemini.py <URL of SSE MCP server> (e.g., http://localhost:8080/sse)"
        )
        sys.exit(1)

    client = GeminiSSEClient()
    try:
        await client.connect_to_sse_server(server_url=sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
