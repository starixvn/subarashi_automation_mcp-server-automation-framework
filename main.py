import asyncio
import logging
import sys
from typing import List, Optional

from config import (
    parse_enhanced_args,
    list_capabilities,
    resolve_enhanced_config,
    config_to_settings,
)
from server import MCPServer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)

logger = logging.getLogger(__name__)


async def main():
    try:
        cli_options = parse_enhanced_args()

        if getattr(cli_options, "list_capabilities", False):
            list_capabilities()
            return

        config = await resolve_enhanced_config(cli_options)

        settings = config_to_settings(config)

        logger.info("Starting MCP Automation Server")
        logger.info(f"Browser: {config.browser.browser_name}")
        logger.info(f"Headless: {config.browser.launch_options.headless}")
        logger.info(f"Vision: {config.vision}")
        logger.info(f"Output Dir: {config.output_dir}")
        logger.info(f"Storage State: {config.browser.context_options.storage_state}")

        if config.capabilities:
            logger.info(f"Capabilities: {', '.join(config.capabilities)}")

        server = MCPServer(settings, capabilities=config.capabilities)

        transport = getattr(cli_options, "transport", "stdio")

        try:
            if transport == "stdio":
                await server.run_stdio()
            elif transport == "websocket":
                host = config.server.host
                port = config.server.port or 8080
                await server.run_websocket(host, port)
            elif transport == "sse":
                host = config.server.host
                port = config.server.port or 8080
                await server.run_sse(host, port)
            elif transport == "http":
                host = config.server.host
                port = config.server.port or 8080
                await server.run_http(host, port)
        except KeyboardInterrupt:
            logger.info("Server interrupted by user")
        except Exception as e:
            logger.error(f"Server error: {e}")
            raise
        finally:
            try:
                await server.cleanup_context()
            except Exception as e:
                logger.error(f"Error during cleanup: {e}")

    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
