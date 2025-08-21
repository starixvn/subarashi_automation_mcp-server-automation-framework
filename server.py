import logging
from typing import List, Optional

from mcp.server.fastmcp import FastMCP
from context import ServerContext
from tools import register_all_tools

logger = logging.getLogger(__name__)


def create_fastmcp_app(
    port: Optional[int] = None,
    host: Optional[str] = None,
    capabilities: Optional[List[str]] = None,
    context: Optional[ServerContext] = None,
) -> FastMCP:
    logger.info("Creating FastMCP app")

    app = FastMCP("MCP Server Automation Framework")
    if port is not None:
        app.settings.port = port
    if host is not None:
        app.settings.host = host

    register_all_tools(app, context, capabilities)
    app._context = context
    if context:
        _register_prompts_and_resources(app, context)

    return app


def _register_prompts_and_resources(app: FastMCP, context: ServerContext):
    logger.info("Registering prompts and resources with FastMCP server")
    if hasattr(context, "prompts") and context.prompts:
        for prompt in context.prompts:
            try:
                app.add_prompt(prompt)
                logger.debug(f"Registered prompt: {prompt.name}")
            except Exception as e:
                logger.error(f"Failed to register prompt {prompt.name}: {e}")
        logger.info(f"Registered {len(context.prompts)} prompts")
    else:
        logger.warning("No prompts found in context to register")

    if hasattr(context, "resources") and context.resources:
        for resource in context.resources:
            try:
                app.add_resource(resource)
                logger.debug(f"Registered resource: {resource.uri}")
            except Exception as e:
                logger.error(f"Failed to register resource {resource.uri}: {e}")
        logger.info(f"Registered {len(context.resources)} resources")
    else:
        logger.warning("No resources found in context to register")
