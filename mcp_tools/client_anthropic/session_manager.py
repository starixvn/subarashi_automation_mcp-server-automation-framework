from typing import Optional, List, Tuple
from contextlib import AsyncExitStack

from mcp import ClientSession
from mcp.client.sse import sse_client


class SessionManager:
    """Manages MCP session connections."""
    
    def __init__(self):
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self._session_context = None
        self._streams_context = None
        
    async def connect(self, server_url: str) -> ClientSession:
        """Connect to an MCP server running with SSE transport.
        
        Args:
            server_url: URL of the SSE server
            
        Returns:
            The connected ClientSession
        """
        # Store the context managers so they stay alive
        self._streams_context = sse_client(url=server_url)
        streams = await self._streams_context.__aenter__()

        self._session_context = ClientSession(*streams)
        self.session = await self._session_context.__aenter__()

        # Initialize
        await self.session.initialize()
        
        return self.session
        
    async def list_tools(self):
        """List available tools on the server."""
        if not self.session:
            raise RuntimeError("Not connected to a server")
            
        response = await self.session.list_tools()
        return response.tools
        
    async def call_tool(self, tool_name: str, tool_args: dict):
        """Call a tool on the server.
        
        Args:
            tool_name: Name of the tool to call
            tool_args: Arguments to pass to the tool
            
        Returns:
            The response from the tool call
        """
        if not self.session:
            raise RuntimeError("Not connected to a server")
            
        return await self.session.call_tool(tool_name, tool_args)
        
    async def cleanup(self):
        """Properly clean up the session and streams."""
        if self._session_context:
            await self._session_context.__aexit__(None, None, None)
        if self._streams_context:
            await self._streams_context.__aexit__(None, None, None) 