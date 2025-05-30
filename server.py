"""
Main entry point for MCP Server.
Provides an SSE-based server for interacting with MCP tools.
"""

from mcp_server.core.mcp_setup import mcp
from mcp_server.config.settings import settings
import argparse
import os
import uvicorn
import logging
from starlette.applications import Starlette
from starlette.routing import Mount, Route
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from mcp.server.sse import SseServerTransport

logging.basicConfig(
    level=getattr(logging, settings.SERVER_LOG_LEVEL),
    format=settings.LOG_FORMAT,
    datefmt=settings.LOG_DATE_FORMAT
)
logger = logging.getLogger(__name__)


def create_starlette_app(*, debug: bool = None) -> Starlette:
    """Create a Starlette application with SSE transport for MCP server."""
    sse = SseServerTransport("/messages/")
    
    debug = debug if debug is not None else settings.SERVER_DEBUG

    async def handle_sse(request: Request):
        """Handle SSE connections following the exact pattern from mcp library documentation."""
        async with sse.connect_sse(
            request.scope,
            request.receive,
            request._send,
        ) as (read_stream, write_stream):
            await mcp._mcp_server.run(
                read_stream,
                write_stream,
                mcp._mcp_server.create_initialization_options(),
            )
        return Response()

    async def health_check(request: Request):
        """Enhanced health check endpoint."""
        return JSONResponse({
            "status": "healthy",
            "service": "Automation Testing Framework",
            "version": "1.0.0",
            "mcp_version": "latest",
            "transport": "sse",
            "endpoints": {
                "sse": "/sse",
                "messages": "/messages/",
                "health": "/health",
                "tools": "/tools"
            },
            "settings": {
                "browser_type": settings.BROWSER_TYPE,
                "browser_headless": settings.BROWSER_HEADLESS,
                "viewport": f"{settings.BROWSER_VIEWPORT_WIDTH}x{settings.BROWSER_VIEWPORT_HEIGHT}",
                "max_concurrent_browsers": settings.MAX_CONCURRENT_BROWSERS
            }
        })

    async def list_tools(request: Request):
        """API endpoint to list available tools."""
        try:
            tools_info = {
                "browser_core_tools": [
                    "browser_navigate", "browser_go_back", "browser_reload", "get_current_url",
                    "browser_click", "browser_fill", "browser_type_advanced", "browser_press_key", 
                    "browser_hover", "browser_find_by_xpath", "browser_select_option", "clear_field",
                    "browser_close", "browser_resize", "browser_install"
                ],
                "browser_advanced_tools": [
                    "browser_drag", "browser_handle_dialog", "browser_console_messages",
                    "browser_scroll_to_top", "browser_scroll_to_bottom", "browser_scroll_to_element", "browser_scroll_one_step",
                    "browser_wait_for"
                ],
                "browser_data_tools": [
                    "get_page_content", "get_page_html", "get_page_title",
                    "clear_browser_data", "get_cookies",
                    "browser_file_upload"
                ],
                "browser_vision_tools": [
                    "browser_capture_for_vision", "browser_save_screenshot", "browser_save_as_pdf",
                    "browser_screen_click", "browser_screen_drag", "browser_screen_move_mouse",
                    "browser_tab_list", "browser_tab_new", "browser_tab_select", "browser_tab_close"
                ],
                "api_tools": [
                    "api_init", "api_get", "api_post", "api_put", "api_delete",
                    "api_basic_auth", "api_bearer_token", "api_oauth2_client_credentials", "api_clear_auth"
                ],
                "database_tools": [
                    "db_connect", "db_connect_with_string", "db_query", "db_execute", "db_execute_many",
                    "db_execute_script", "db_get_tables", "db_get_columns", "db_close"
                ],
                "google_tools": [
                    "google_sheets_init", "google_sheets_read", "google_sheets_write",
                    "google_sheets_append", "google_sheets_clear", "google_sheets_create_sheet", "google_sheets_get_sheets"
                ]
            }
            
            return JSONResponse({
                "framework": "MCP Automation Testing Framework",
                "total_tools": sum(len(tools) for tools in tools_info.values()),
                "tools_by_category": tools_info,
                "tool_counts": {
                    "browser_core_tools": len(tools_info["browser_core_tools"]),
                    "browser_advanced_tools": len(tools_info["browser_advanced_tools"]), 
                    "browser_data_tools": len(tools_info["browser_data_tools"]),
                    "browser_vision_tools": len(tools_info["browser_vision_tools"]),
                    "api_tools": len(tools_info["api_tools"]),
                    "database_tools": len(tools_info["database_tools"]),
                    "google_tools": len(tools_info["google_tools"])
                },
                "configuration": {
                    "timeouts": {
                        "browser_navigation": settings.BROWSER_NAVIGATION_TIMEOUT,
                        "browser_click": settings.BROWSER_CLICK_TIMEOUT,
                        "api_request": settings.API_REQUEST_TIMEOUT,
                        "database_query": settings.DATABASE_QUERY_TIMEOUT
                    },
                    "limits": {
                        "max_url_length": settings.MAX_URL_LENGTH,
                        "max_selector_length": settings.MAX_SELECTOR_LENGTH,
                        "max_xpath_length": settings.MAX_XPATH_LENGTH
                    }
                }
            })
        except Exception as e:
            logger.error(f"Error listing tools: {e}")
            return JSONResponse({"error": str(e)}, status_code=500)

    return Starlette(
        debug=debug,
        routes=[
            Route("/sse", endpoint=handle_sse, methods=["GET"]),
            Route("/health", endpoint=health_check, methods=["GET"]),
            Route("/tools", endpoint=list_tools, methods=["GET"]),
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )


def main():
    """Run the MCP server with improved configuration."""
    parser = argparse.ArgumentParser(
        description="MCP Automation Testing Framework Server"
    )
    parser.add_argument(
        "--host", 
        default=settings.SERVER_HOST, 
        help=f"Host to bind to (default: {settings.SERVER_HOST})"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=int(os.environ.get("PORT", str(settings.SERVER_PORT))), 
        help=f"Port to listen on (default: {settings.SERVER_PORT})"
    )
    parser.add_argument(
        "--debug", 
        action="store_true",
        default=settings.SERVER_DEBUG,
        help="Enable debug mode"
    )
    args = parser.parse_args()

    if not 1 <= args.port <= 65535:
        raise ValueError(f"Invalid port: {args.port}")

    starlette_app = create_starlette_app(debug=args.debug)

    logger.info(f" Starting MCP Automation Testing Framework server on {args.host}:{args.port}")
    logger.info(f" Transport: Server-Sent Events (SSE)")
    logger.info(f" SSE Endpoint: http://{args.host}:{args.port}/sse")
    logger.info(f" Messages Endpoint: http://{args.host}:{args.port}/messages/")
    logger.info(f" Health Check: http://{args.host}:{args.port}/health")
    logger.info(f" Tools List: http://{args.host}:{args.port}/tools")
    logger.info(f"Configuration loaded from settings:")
    logger.info(f"  - Browser: {settings.BROWSER_TYPE} ({'headless' if settings.BROWSER_HEADLESS else 'headed'})")
    logger.info(f"  - Viewport: {settings.BROWSER_VIEWPORT_WIDTH}x{settings.BROWSER_VIEWPORT_HEIGHT}")
    logger.info(f"  - Output directory: {settings.OUTPUT_DIRECTORY}")
    logger.info(f"  - Debug mode: {args.debug}")
    
    uvicorn.run(
        starlette_app, 
        host=args.host, 
        port=args.port,
        log_level="debug" if args.debug else settings.SERVER_LOG_LEVEL.lower(),
        access_log=args.debug
    )


if __name__ == "__main__":
    main()
