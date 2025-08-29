import logging
import datetime
from typing import List
from mcp.server.fastmcp.resources import Resource
from mcp.server.fastmcp.resources import (
    TextResource,
    FunctionResource,
)
from pydantic import AnyUrl

logger = logging.getLogger(__name__)


def get_default_resources() -> List[Resource]:
    resources = []

    try:
        example_text = TextResource(
            uri=AnyUrl("internal://example/welcome"),
            name="Welcome Message",
            description="A welcome message for the MCP server",
            text="Welcome to the MCP Browser Automation Server!",
        )
        resources.append(example_text)
    except Exception as e:
        logger.warning(f"Could not create example text resource: {e}")

    def get_server_info() -> str:
        return (
            f"Server status: Running\nTimestamp: {datetime.datetime.now().isoformat()}"
        )

    try:
        server_info = FunctionResource.from_function(
            fn=get_server_info,
            uri="internal://server/info",
            name="Server Information",
            description="Current server status and information",
            mime_type="text/plain",
        )
        resources.append(server_info)
    except Exception as e:
        logger.warning(f"Could not create server info resource: {e}")

    logger.info(f"Created {len(resources)} default FastMCP resources")
    return resources


def get_resource_by_uri(uri: str) -> Resource | None:
    resources = get_default_resources()
    for resource in resources:
        if str(resource.uri) == uri:
            return resource
    return None
