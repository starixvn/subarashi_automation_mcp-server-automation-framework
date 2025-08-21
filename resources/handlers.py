import logging
from typing import Dict, List, Optional, Callable, TYPE_CHECKING
from mcp.types import Resource as MCPResource, ReadResourceResult, TextResourceContents

from .registry import get_default_resources, get_resource_by_uri

if TYPE_CHECKING:
    from context import ServerContext

logger = logging.getLogger(__name__)


def get_resources_handlers(
    context: Optional["ServerContext"] = None,
) -> Dict[str, Callable]:
    async def list_resources() -> List[MCPResource]:
        try:
            resources = get_default_resources()
            mcp_resources = []
            for resource in resources:
                mcp_resource = MCPResource(
                    uri=resource.uri,
                    name=resource.name or str(resource.uri),
                    description=resource.description,
                    mimeType=resource.mime_type,
                )
                mcp_resources.append(mcp_resource)

            logger.debug(f"Listed {len(mcp_resources)} FastMCP resources")
            return mcp_resources

        except Exception as e:
            logger.error(f"Error listing resources: {e}")
            return []

    async def read_resource(uri: str) -> ReadResourceResult:
        try:
            resource = get_resource_by_uri(uri)
            if not resource:
                raise ValueError(f"Resource not found: {uri}")

            content = await resource.read()

            if isinstance(content, str):
                mcp_contents = [
                    TextResourceContents(
                        uri=resource.uri, mimeType=resource.mime_type, text=content
                    )
                ]
            else:
                mcp_contents = [
                    TextResourceContents(
                        uri=resource.uri, mimeType=resource.mime_type, text=str(content)
                    )
                ]

            result = ReadResourceResult(contents=mcp_contents)
            logger.debug(f"Read FastMCP resource {uri}")
            return result

        except Exception as e:
            logger.error(f"Error reading resource {uri}: {e}")
            return ReadResourceResult(contents=[])

    async def subscribe_resource(uri: str) -> None:
        try:
            logger.debug(
                f"Subscribe request for resource {uri} (not implemented in FastMCP)"
            )

        except Exception as e:
            logger.error(f"Error subscribing to resource {uri}: {e}")

    async def unsubscribe_resource(uri: str) -> None:
        try:
            logger.debug(
                f"Unsubscribe request for resource {uri} (not implemented in FastMCP)"
            )

        except Exception as e:
            logger.error(f"Error unsubscribing from resource {uri}: {e}")

    return {
        "list_resources": list_resources,
        "read_resource": read_resource,
        "subscribe_resource": subscribe_resource,
        "unsubscribe_resource": unsubscribe_resource,
    }
