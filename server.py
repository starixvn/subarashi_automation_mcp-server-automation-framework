"""
Main entry point for MCP Server.
Provides an SSE-based server for interacting with MCP tools.
"""

from mcp_server.core.mcp_setup import mcp
import argparse
import os
import uvicorn
from mcp.server import Server
from starlette.applications import Starlette
from starlette.routing import Mount, Route
from starlette.requests import Request
from starlette.responses import Response
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from mcp.server.sse import SseServerTransport


def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    """Create a Starlette application with SSE transport for MCP server."""
    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request):
        """Handle SSE connections."""
        async with sse.connect_sse(
            request.scope,
            request.receive,
            request._send,
        ) as (read_stream, write_stream):
            await mcp_server.run(
                read_stream,
                write_stream,
                mcp_server.create_initialization_options(),
            )
        return Response()

    async def health_check(request: Request):
        """Health check endpoint."""
        return Response(content="OK", media_type="text/plain")

    # Allow CORS from all origins for development
    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
        )
    ]

    return Starlette(
        debug=debug,
        middleware=middleware,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Route("/health", endpoint=health_check),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )


def main():
    """Run the MCP server."""
    mcp_server = mcp._mcp_server
    parser = argparse.ArgumentParser(description="Run MCP SSE-based server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", "5000")), help="Port to listen on")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()

    # Bind SSE request handling to MCP server
    starlette_app = create_starlette_app(mcp_server, debug=args.debug)

    uvicorn.run(starlette_app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
