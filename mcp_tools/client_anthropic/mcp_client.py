import asyncio
from typing import Optional, List

from mcp_tools.client_anthropic.anthropic_service import AnthropicService
from mcp_tools.client_anthropic.session_manager import SessionManager
from mcp_tools.client_anthropic.query_processor import QueryProcessor


class MCPClient:
    """Main client for interacting with MCP servers."""

    def __init__(self):
        """Initialize the MCP client."""
        self.session_manager = SessionManager()
        self.anthropic_service = AnthropicService()
        self.query_processor = QueryProcessor(
            session_manager=self.session_manager,
            anthropic_service=self.anthropic_service,
        )

    async def connect_to_sse_server(self, server_url: str):
        """Connect to an MCP server running with SSE transport.

        Args:
            server_url: URL of the SSE server
        """
        await self.session_manager.connect(server_url)

        # List available tools to verify connection
        print("Initialized SSE client...")
        print("Listing tools...")
        tools = await self.session_manager.list_tools()
        print("\nConnected to server with tools:", [tool.name for tool in tools])

    async def process_query(self, query: str) -> str:
        """Process a query using Claude and available tools.

        Args:
            query: The user's query

        Returns:
            The final response text
        """
        return await self.query_processor.process_query(query)

    async def chat_loop(self):
        """Run an interactive chat loop."""
        print("\nMCP Client Started!")
        print("Type your queries or 'quit' to exit.")

        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() == "quit":
                    break

                response = await self.process_query(query)
                print("\n" + response)

            except Exception as e:
                print(f"\nError: {str(e)}")

    async def cleanup(self):
        """Properly clean up the session and streams."""
        await self.session_manager.cleanup()
