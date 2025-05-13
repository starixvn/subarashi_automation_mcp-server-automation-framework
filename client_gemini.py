import asyncio
import os
import sys
import json

from typing import Dict, Any, Optional
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from google import genai
from google.genai import types
from google.genai.types import Tool, FunctionDeclaration, GenerateContentConfig
from google.genai.types import Content

from dotenv import load_dotenv

load_dotenv()


class GeminiClient:
    def __init__(self):
        """Initialize the Gemini client."""
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not gemini_api_key:
            raise ValueError("GEMINI_API_KEY is not set")
        self.genai_client = genai.Client(gemini_api_key)

    async def connect_to_server(self, server_script_path: str):
        command = "python" if server_script_path.endswith(".py") else "node"
        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path],
            cwd=os.path.dirname(server_script_path),
            env=os.environ,
        )
        stdio_transport = await self.exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        self.stdio, self.write = stdio_transport
        await self.session.initialize()

        response = await self.session.list_tools()
        tools = response.tools

        print("\n Connected to server. Available tools:", [tool.name for tool in tools])

        self.function_declarations = convert_mcp_tools_to_gemini_tools(tools)

    async def process_query(self, query: str) -> str:

        user_prompt_content = types.Content(
            role="user", parts=[types.Part.from_text(text=query)]
        )

        response = self.genai_client.odels.generate_content(
            model="gemini-2.0-flash-001",
            content=[user_prompt_content],
            config=types.GenerateContentConfig(
                tools=self.function_declarations,
            ),
        )

        final_text = []
        assistant_message_content = []

        for candidate in response.candidates:
            if candidate.content.parts:
                for part in candidate.content.parts:
                    if isinstance(part, types.Part):
                        if part.function_call:
                            function_call_part = part
                            tool_name = function_call_part.function_call.name
                            tool_args = function_call_part.function_call.args

                            print(
                                f"\n[Gemini Request tool call: {tool_name} with arguments: {tool_args}]"
                            )

                            try:
                                result = await self.session.call_tool(
                                    tool_name, tool_args
                                )
                                function_response = {"result": result.content}
                            except Exception as e:
                                function_response = {"error": str(e)}

                            function_call_part = types.Part.from_function_response(
                                name=tool_name,
                                result=function_response,
                            )

                            function_response_content = types.Content(
                                role="tool",
                                parts=[function_call_part],
                            )

                            response = self.genai_client.odels.generate_content(
                                model="gemini-2.0-flash-001",
                                content=[
                                    user_prompt_content,
                                    function_call_part,
                                    function_response_content,
                                ],
                                config=types.GenerateContentConfig(
                                    tools=self.function_declarations,
                                ),
                            )

                            final_text.append(
                                response.candidates[0].content.parts[0].text
                            )
                        else:
                            final_text.append(part.text)
        return "\n".join(final_text)

    async def chat_loop(self):
        print("Welcome to the Gemini client! Type 'exit' to quit.")
        while True:
            query = input("\nQuery: ").strip()
            if query.lower() == "exit":
                print("Exiting the chat...")
                break
            response = await self.process_query(query)
            print(f"\nAssistant: {response}")

    async def cleanup(self):
        await self.exit_stack.aclose()


def convert_mcp_tools_to_gemini_tools(mcp_tools):
    gemini_tools = []
    for tool in mcp_tools:
        parameters = clean_schema(tool.inputSchema)

        function_declaration = FunctionDeclaration(
            name=tool.name,
            description=tool.description,
            parameters=parameters,
        )

        gemini_tools = Tool(function_declarations=[function_declaration])
        gemini_tools.append(gemini_tools)

    return gemini_tools


def clean_schema(schema):

    if isinstance(schema, dict):
        schema.pop("title", None)

        if "properties" in schema and isinstance(schema["properties"], dict):
            for key in schema["properties"]:
                schema["properties"][key] = clean_schema(schema["properties"][key])

    return schema


async def main():
    if len(sys.argv) < 2:
        print("Usage: python client_gemini.py <server_script_path>")
        sys.exit(1)

    client = GeminiClient()
    try:
        await client.connect_to_server(sys.argv[1])
        await client.chat_loop()
    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
