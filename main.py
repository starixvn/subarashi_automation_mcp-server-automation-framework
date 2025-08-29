import asyncio
import logging
import sys

from config import (
    parse_enhanced_args,
    list_capabilities,
    resolve_enhanced_config,
)
from server import create_fastmcp_app
from context import ServerContext

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

        logger.info(
            f"MCP Server ready on {config.server.host or '127.0.0.1'}:{config.server.port or 8000}"
        )
        if config.capabilities:
            logger.info(f"Capabilities: {', '.join(config.capabilities)}")
        else:
            logger.info("Capabilities: all")
        port = config.server.port or 8000
        host = config.server.host or "127.0.0.1"
        context = ServerContext(config, capabilities=config.capabilities)
        app = create_fastmcp_app(
            port=port, host=host, capabilities=config.capabilities, context=context
        )

        transport = getattr(cli_options, "transport", "stdio")

        try:
            await context.start()
            if transport == "stdio":
                await app.run_stdio_async()
            elif transport == "sse":
                await app.run_sse_async()
            elif transport in ["http", "streamable-http"]:
                await app.run_streamable_http_async()
            else:
                raise ValueError(f"Unknown transport: {transport}")
        except KeyboardInterrupt:
            logger.info("Server interrupted by user")
        except Exception as e:
            logger.error(f"Server error: {e}")
            raise
        finally:
            await context.close()
            logger.info("Server finished")

    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
