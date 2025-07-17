import json
import logging
from contextlib import asynccontextmanager
from http import HTTPStatus

import anyio
from anyio.streams.memory import MemoryObjectReceiveStream, MemoryObjectSendStream
from pydantic import ValidationError
from starlette.requests import Request
from starlette.responses import Response

import mcp.types as types
from mcp.shared.message import SessionMessage

logger = logging.getLogger(__name__)
MAXIMUM_MESSAGE_SIZE = 4 * 1024 * 1024  # 4MB

MCP_SESSION_ID_HEADER = "mcp-session-id"
CONTENT_TYPE_JSON = "application/json"


class StreamableHTTPServerTransport:
    def __init__(
        self,
        mcp_session_id: str | None,
        is_json_response_enabled: bool = True,
        event_store=None,
    ) -> None:
        self.mcp_session_id = mcp_session_id
        self.is_json_response_enabled = is_json_response_enabled
        self._event_store = event_store
        self._terminated = False

    @asynccontextmanager
    async def connect(self):
        read_stream_writer, read_stream = anyio.create_memory_object_stream[
            SessionMessage | Exception
        ](0)
        write_stream, write_stream_reader = anyio.create_memory_object_stream[
            SessionMessage
        ](0)

        try:
            yield read_stream, write_stream
        finally:
            try:
                await read_stream_writer.aclose()
                await read_stream.aclose()
                await write_stream_reader.aclose()
                await write_stream.aclose()
            except Exception as e:
                logger.debug(f"Error closing streams: {e}")

    async def handle_request(self, scope, receive, send) -> None:
        request = Request(scope, receive)

        if self._terminated:
            response = Response(
                "Not Found: Session has been terminated",
                status_code=HTTPStatus.NOT_FOUND,
            )
            await response(scope, receive, send)
            return

        if request.method == "POST":
            await self._handle_post_request(scope, request, receive, send)
        elif request.method == "GET":
            await self._handle_get_request(request, send)
        else:
            await self._handle_unsupported_request(request, send)

    async def _handle_post_request(
        self, scope, request: Request, receive, send
    ) -> None:
        try:
            body = await request.body()
            if len(body) > MAXIMUM_MESSAGE_SIZE:
                response = Response(
                    "Payload Too Large: Message exceeds maximum size",
                    status_code=HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
                )
                await response(scope, receive, send)
                return

            try:
                raw_message = json.loads(body)
            except json.JSONDecodeError as e:
                response = Response(
                    f"Parse error: {str(e)}",
                    status_code=HTTPStatus.BAD_REQUEST,
                )
                await response(scope, receive, send)
                return

            try:
                message = types.JSONRPCMessage.model_validate(raw_message)
            except ValidationError as e:
                response = Response(
                    f"Validation error: {str(e)}",
                    status_code=HTTPStatus.BAD_REQUEST,
                )
                await response(scope, receive, send)
                return

            if isinstance(message.root, types.JSONRPCRequest):
                if message.root.method == "initialize":
                    result = {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {
                            "name": "mcp-automation-server",
                            "version": "1.0.0",
                        },
                    }
                    response_data = {
                        "jsonrpc": "2.0",
                        "id": message.root.id,
                        "result": result,
                    }
                elif message.root.method == "tools/list":
                    response_data = {
                        "jsonrpc": "2.0",
                        "id": message.root.id,
                        "result": {"tools": []},
                    }
                else:
                    response_data = {
                        "jsonrpc": "2.0",
                        "id": message.root.id,
                        "error": {
                            "code": -32601,
                            "message": f"Method not found: {message.root.method}",
                        },
                    }

                response = Response(
                    json.dumps(response_data),
                    status_code=HTTPStatus.OK,
                    headers={"Content-Type": CONTENT_TYPE_JSON},
                )
                await response(scope, receive, send)
            else:
                response = Response(
                    None,
                    status_code=HTTPStatus.ACCEPTED,
                    headers={"Content-Type": CONTENT_TYPE_JSON},
                )
                await response(scope, receive, send)

        except Exception as err:
            logger.exception("Error handling POST request")
            response = Response(
                f"Error handling POST request: {err}",
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            )
            await response(scope, receive, send)

    async def _handle_get_request(self, request: Request, send) -> None:
        response = Response(
            "Method Not Allowed: Use POST for requests",
            status_code=HTTPStatus.METHOD_NOT_ALLOWED,
        )
        await response(request.scope, request.receive, send)

    async def _handle_unsupported_request(self, request: Request, send) -> None:
        response = Response(
            "Method Not Allowed",
            status_code=HTTPStatus.METHOD_NOT_ALLOWED,
            headers={"Allow": "GET, POST"},
        )
        await response(request.scope, request.receive, send)


class StreamableHTTPSessionManager:
    def __init__(self, app, event_store=None, json_response=True, stateless=True):
        self.app = app
        self.event_store = event_store
        self.json_response = json_response
        self.stateless = stateless
        self._task_group = None

    @asynccontextmanager
    async def run(self):
        async with anyio.create_task_group() as tg:
            self._task_group = tg
            logger.info("StreamableHTTP session manager started")
            try:
                yield
            finally:
                logger.info("StreamableHTTP session manager shutting down")
                tg.cancel_scope.cancel()
                self._task_group = None

    async def handle_request(self, scope, receive, send) -> None:
        if self._task_group is None:
            raise RuntimeError("Task group is not initialized. Make sure to use run().")

        transport = StreamableHTTPServerTransport(
            mcp_session_id=None,
            is_json_response_enabled=self.json_response,
        )

        await transport.handle_request(scope, receive, send)
