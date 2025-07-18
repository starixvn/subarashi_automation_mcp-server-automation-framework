import asyncio
import logging
import signal
import sys
import traceback
import uvicorn
from typing import Any, Dict, List, Optional

import anyio
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import (
    ServerCapabilities,
    Implementation,
    Tool,
    TextContent,
    CallToolResult,
    ImageContent,
    Prompt,
    PromptMessage,
    GetPromptResult,
    Resource,
    ReadResourceResult,
)
from prompts.handlers import get_prompts_handlers
from resources.handlers import get_resources_handlers
from mcp.server.models import ServerCapabilities
from mcp.server.stdio import stdio_server
from transports import websocket_server
from starlette.routing import WebSocketRoute
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import Response, JSONResponse
from mcp.server.streamable_http import StreamableHTTPServerTransport


from config.settings import Settings
from context import ServerContext

logger = logging.getLogger(__name__)


def create_server(
    settings: Optional[Settings] = None,
    capabilities: Optional[List[str]] = None,
    context: Optional[ServerContext] = None,
) -> Server:
    if settings is None:
        settings = Settings()

    if context is None:
        context = ServerContext(settings, capabilities=capabilities)

    server = Server("mcp-automation-server")

    prompts_handlers = get_prompts_handlers()
    resources_handlers = get_resources_handlers(context)

    @server.list_tools()
    async def list_tools() -> List[Tool]:
        tools_schema = context.tool_registry.get_mcp_tools_schema()
        return [
            Tool(
                name=tool_schema["name"],
                description=tool_schema["description"],
                inputSchema=tool_schema["inputSchema"],
            )
            for tool_schema in tools_schema
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
        try:
            tool_info = next(
                (
                    tool
                    for tool in await context.tool_registry.list_tools()
                    if tool["name"] == name
                ),
                None,
            )

            if not tool_info:
                return [TextContent(type="text", text=f'Tool "{name}" not found')]

            modal_states = [state.type for state in context.modal_states()]

            tool_clears_modal = tool_info.get("clearsModalState")
            if tool_clears_modal and tool_clears_modal not in modal_states:
                error_messages = [
                    f'The tool "{name}" can only be used when there is related modal state present.'
                ]
                error_messages.extend(context.modal_states_markdown())
                return [TextContent(type="text", text="\n".join(error_messages))]

            if not tool_clears_modal and modal_states:
                error_messages = [f'Tool "{name}" does not handle the modal state.']
                error_messages.extend(context.modal_states_markdown())
                return [TextContent(type="text", text="\n".join(error_messages))]

            result = await context.tool_registry.execute_tool(name, arguments)

            content = []
            if result and result.content:
                for item in result.content:
                    if item.get("type") == "text":
                        content.append(TextContent(type="text", text=item["text"]))
                    elif item.get("type") == "image":
                        content.append(
                            ImageContent(
                                type="image",
                                data=item["data"],
                                mimeType=item["mimeType"],
                            )
                        )

            if not content:
                content = [TextContent(type="text", text="Tool executed successfully")]

            return content

        except Exception as e:
            logger.error(f"Error executing tool {name}: {e}")
            return [
                TextContent(type="text", text=f"Error executing tool {name}: {str(e)}")
            ]

    @server.list_prompts()
    async def list_prompts() -> List[Prompt]:
        return await prompts_handlers["list_prompts"]()

    @server.get_prompt()
    async def get_prompt(
        name: str, arguments: Optional[Dict[str, Any]] = None
    ) -> GetPromptResult:
        return await prompts_handlers["get_prompt"](name, arguments)

    @server.list_resources()
    async def list_resources() -> List[Resource]:
        return await resources_handlers["list_resources"]()

    @server.read_resource()
    async def read_resource(uri: str) -> ReadResourceResult:
        return await resources_handlers["read_resource"](uri)

    return server


class MCPServer:
    def __init__(
        self,
        settings: Optional[Settings] = None,
        capabilities: Optional[List[str]] = None,
    ):
        self.settings = settings or Settings()
        self.capabilities = capabilities
        self.context = ServerContext(self.settings, capabilities=capabilities)
        self.server = create_server(self.settings, capabilities, self.context)
        self._context_initialized = False

        def on_initialized():
            if hasattr(self.server, "_session") and hasattr(
                self.server._session, "client_info"
            ):
                client_info = self.server._session.client_info
                if client_info:
                    self.context.clientVersion = {
                        "name": client_info.name,
                        "version": client_info.version,
                    }

        if hasattr(self.server, "set_initialized_callback"):
            self.server.set_initialized_callback(on_initialized)

    async def _ensure_context_started(self):
        if not self._context_initialized:
            await self.context.start()
            self._context_initialized = True
            logger.info("Browser context initialized successfully")

    def create_initialization_options(self) -> InitializationOptions:
        return InitializationOptions(
            server_name="mcp-automation-server",
            server_version="1.0.0",
            capabilities=ServerCapabilities(
                tools={"listChanged": True},
                prompts={"listChanged": True},
                resources={"subscribe": True, "listChanged": True},
                logging={},
            ),
        )

    def setup_exit_watchdog(self):
        def handle_exit():
            logger.info("Server shutting down...")
            try:
                asyncio.run(self.context.close())
            except Exception as e:
                logger.error(f"Error during shutdown: {e}")
            sys.exit(0)

        signal.signal(signal.SIGINT, lambda s, f: handle_exit())
        signal.signal(signal.SIGTERM, lambda s, f: handle_exit())

    async def run_stdio(self):
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream, write_stream, self.create_initialization_options()
            )

    async def run_websocket(self, host: str = "localhost", port: int = 8765):
        async def websocket_endpoint(websocket):
            await websocket.accept()
            async with websocket_server(
                websocket.scope, websocket.receive, websocket.send
            ) as (read_stream, write_stream):
                await self.server.run(
                    read_stream, write_stream, self.create_initialization_options()
                )

        app = Starlette(routes=[WebSocketRoute("/", websocket_endpoint)])

        config = uvicorn.Config(app, host=host, port=port, log_level="info")
        server = uvicorn.Server(config)
        await server.serve()

    async def run_sse(self, host: str = "localhost", port: int = 8080):
        logging.getLogger("mcp").setLevel(logging.INFO)
        logging.getLogger("mcp.server").setLevel(logging.INFO)
        logging.getLogger("mcp.server.session").setLevel(logging.INFO)

        sse_transport = SseServerTransport("/messages")

        async def handle_sse(request):
            logger.info("New SSE connection established")
            try:
                async with sse_transport.connect_sse(
                    request.scope, request.receive, request._send
                ) as (read_stream, write_stream):
                    logger.info("Starting MCP server with initialization options")
                    await self.server.run(
                        read_stream, write_stream, self.create_initialization_options()
                    )
            except (Exception, asyncio.CancelledError) as e:
                if isinstance(e, asyncio.CancelledError):
                    logger.info("SSE connection cancelled by client")
                else:
                    logger.error(f"Error in SSE connection: {e}")
                    traceback.print_exc()
                logger.info("SSE connection closed")
            return Response()

        async def handle_messages(scope, receive, send):
            await sse_transport.handle_post_message(scope, receive, send)

        async def health_endpoint(request):
            return JSONResponse(
                {
                    "status": "ok",
                    "service": "mcp-automation-server",
                    "version": "1.0.0",
                    "transport": "sse",
                }
            )

        async def root_endpoint(request):
            return JSONResponse(
                {
                    "service": "MCP Automation Server",
                    "version": "1.0.0",
                    "transport": "sse",
                    "status": "running",
                    "endpoints": {
                        "health": "/health",
                        "sse": "/sse",
                        "messages": "/messages",
                    },
                    "capabilities": self.context.capabilities
                    if hasattr(self.context, "capabilities")
                    else [],
                    "description": "Model Context Protocol Server for Browser Automation",
                }
            )

        app = Starlette(
            routes=[
                Route("/", endpoint=root_endpoint, methods=["GET"]),
                Route("/sse", endpoint=handle_sse, methods=["GET"]),
                Route("/health", endpoint=health_endpoint, methods=["GET"]),
            ]
        )

        original_app = app

        async def app_with_messages(scope, receive, send):
            if (
                scope["type"] == "http"
                and scope["path"] == "/messages"
                and scope["method"] == "POST"
            ):
                await handle_messages(scope, receive, send)
            else:
                await original_app(scope, receive, send)

        logger.info(f"Starting SSE server on {host}:{port}")
        config = uvicorn.Config(
            app_with_messages, host=host, port=port, log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()

    async def run_http(self, host: str = "localhost", port: int = 8080):
        transport = StreamableHTTPServerTransport(
            mcp_session_id=None, is_json_response_enabled=True
        )

        async def run_mcp_server():
            async with transport.connect() as (read_stream, write_stream):
                await self.server.run(
                    read_stream, write_stream, self.create_initialization_options()
                )

        async def mcp_endpoint(request):
            await transport.handle_request(
                request.scope, request.receive, request._send
            )

        async def health_endpoint(request):
            return JSONResponse(
                {
                    "status": "ok",
                    "service": "mcp-automation-server",
                    "version": "1.0.0",
                    "transport": "http",
                }
            )

        async def root_endpoint(request):
            return JSONResponse(
                {
                    "service": "MCP Automation Server",
                    "version": "1.0.0",
                    "transport": "http",
                    "status": "running",
                    "endpoints": {"health": "/health", "mcp": "/mcp"},
                    "capabilities": self.context.capabilities
                    if hasattr(self.context, "capabilities")
                    else [],
                    "description": "Model Context Protocol Server for Browser Automation",
                }
            )

        app = Starlette(
            routes=[
                Route("/", endpoint=root_endpoint, methods=["GET"]),
                Route("/mcp", mcp_endpoint, methods=["GET", "POST", "DELETE"]),
                Route("/health", health_endpoint, methods=["GET"]),
            ]
        )

        async with anyio.create_task_group() as tg:
            tg.start_soon(run_mcp_server)

            config = uvicorn.Config(app, host=host, port=port, log_level="info")
            server = uvicorn.Server(config)
            await server.serve()
