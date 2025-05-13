"""
MCP Server with Ngrok public URL access.
"""

from mcp_tools.server import mcp
import argparse
import uvicorn
from mcp.server import Server
from starlette.applications import Starlette
from starlette.routing import Mount, Route, WebSocketRoute
from starlette.requests import Request
from starlette.responses import Response
from mcp.server.sse import SseServerTransport
import atexit
import logging
import os
import subprocess
import tempfile
import time
import json
from dotenv import load_dotenv
import pathlib
from starlette.websockets import WebSocket


load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    """Create a Starlette application that can server the provied mcp server with SSE."""
    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request):
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

    async def handle_custom_message(websocket: WebSocket):
        """Handle custom WebSocket messages for browser delegation."""
        await websocket.accept()
        try:
            while True:
                data = await websocket.receive_text()
                message = json.loads(data)
                # Pass message to MCP server for processing
                await mcp_server.process_custom_message(message)
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
        finally:
            await websocket.close()

    return Starlette(
        debug=debug,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
            WebSocketRoute("/ws", endpoint=handle_custom_message),
        ],
    )


def start_ngrok_direct(port, auth_token=None):
    temp_dir = tempfile.mkdtemp()
    logger.info(f"Using temporary config directory: {temp_dir}")

    base_path = pathlib.Path(__file__).parent.absolute()
    ngrok_path = os.path.join(base_path, "ngrok", "ngrok.exe")

    if not os.path.exists(ngrok_path):
        raise FileNotFoundError(f"Could not find ngrok.exe at {ngrok_path}")

    logger.info(f"Using ngrok from: {ngrok_path}")

    if auth_token:
        logger.info(f"Using ngrok authentication token")
        config_path = os.path.join(temp_dir, "ngrok.yml")
        with open(config_path, "w") as f:
            f.write(f"authtoken: {auth_token}\n")

        subprocess.run(
            [ngrok_path, "config", "add-authtoken", auth_token],
            check=False,
            capture_output=True,
        )

    ngrok_cmd = [ngrok_path, "http", str(port)]

    log_file = os.path.join(temp_dir, "ngrok_log.txt")
    with open(log_file, "w") as log:
        ngrok_process = subprocess.Popen(
            ngrok_cmd, stdout=log, stderr=subprocess.STDOUT, text=True, cwd=temp_dir
        )

    logger.info("Waiting for ngrok to start...")
    time.sleep(3)

    if ngrok_process.poll() is not None:
        with open(log_file, "r") as log:
            error_output = log.read()
            logger.error(f"Ngrok failed to start. Log:\n{error_output}")
        raise Exception(f"Ngrok exited with code {ngrok_process.returncode}")

    public_url = None
    for i in range(10):
        try:
            api_result = subprocess.run(
                ["curl", "-s", "http://localhost:4040/api/tunnels"],
                capture_output=True,
                text=True,
            )

            if api_result.returncode == 0 and api_result.stdout:
                try:
                    data = json.loads(api_result.stdout)
                    if data and "tunnels" in data and data["tunnels"]:
                        public_url = data["tunnels"][0]["public_url"]
                        logger.info(f"🌐 NGROK PUBLIC URL: {public_url}")
                        logger.info(f"📱 CLIENT CONNECTION URL: {public_url}/sse")

                        with open("ngrok_url.txt", "w") as f:
                            f.write(
                                f"Public URL: {public_url}\nClient URL: {public_url}/sse"
                            )

                        atexit.register(
                            lambda: subprocess.run(
                                ["taskkill", "/f", "/im", "ngrok.exe"],
                                stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL,
                            )
                        )

                        return public_url
                except json.JSONDecodeError:
                    pass
        except Exception as e:
            logger.debug(f"API check error: {e}")

        time.sleep(1)

    logger.error("Could not obtain ngrok URL after multiple attempts")

    with open(log_file, "r") as log:
        ngrok_output = log.read()
        logger.error(f"Ngrok log:\n{ngrok_output}")

    if ngrok_process.poll() is None:
        ngrok_process.terminate()

    raise Exception("Failed to get ngrok public URL")


if __name__ == "__main__":
    mcp_server = mcp._mcp_server
    parser = argparse.ArgumentParser(description="Run MCP SSE-based server with Ngrok")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8080, help="Port to listen on")
    parser.add_argument("--no-ngrok", action="store_true", help="Disable Ngrok tunnel")
    parser.add_argument("--ngrok-token", help="Ngrok authentication token")
    args = parser.parse_args()
    ngrok_token = args.ngrok_token or os.getenv("NGROK_AUTH_TOKEN")

    if not args.no_ngrok:
        try:
            start_ngrok_direct(args.port, ngrok_token)
            logger.info("MCP Server exposed via Ngrok")
        except Exception as e:
            logger.error(f"Cannot start Ngrok: {str(e)}")
            logger.info("Starting server on localhost only...")

    starlette_app = create_starlette_app(mcp_server, debug=True)
    logger.info(f"Starting local server on {args.host}:{args.port}")
    uvicorn.run(starlette_app, host=args.host, port=args.port)
