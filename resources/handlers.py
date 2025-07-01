import logging
from typing import Dict, List, Optional, Any, Callable, TYPE_CHECKING
from mcp.types import Resource as MCPResource, ReadResourceResult

from .registry import resource_registry

if TYPE_CHECKING:
    from context import ServerContext

logger = logging.getLogger(__name__)


def get_resources_handlers(context: Optional["ServerContext"] = None) -> Dict[str, Callable]:

    async def list_resources() -> List[MCPResource]:
        
        try:
            registry = context.resource_registry if context else resource_registry
            resources = await registry.list_resources()
            mcp_resources = [resource.to_mcp_resource() for resource in resources]
            
            logger.debug(f"Listed {len(mcp_resources)} resources")
            return mcp_resources
            
        except Exception as e:
            logger.error(f"Error listing resources: {e}")
            return []
    
    async def read_resource(uri: str) -> ReadResourceResult:
        
        try:
            registry = context.resource_registry if context else resource_registry
            result = await registry.read_resource(uri)
            
            logger.debug(f"Read resource {uri}")
            return result
            
        except Exception as e:
            logger.error(f"Error reading resource {uri}: {e}")
            return ReadResourceResult(contents=[])
    
    async def subscribe_resource(uri: str) -> None:
        
        try:
            registry = context.resource_registry if context else resource_registry
            success = await registry.subscribe_to_resource(uri, lambda x: None)
            
            if success:
                logger.debug(f"Subscribed to resource {uri}")
            else:
                logger.warning(f"Failed to subscribe to resource {uri}")
                
        except Exception as e:
            logger.error(f"Error subscribing to resource {uri}: {e}")
    
    async def unsubscribe_resource(uri: str) -> None:
        
        try:
            registry = context.resource_registry if context else resource_registry
            success = await registry.unsubscribe_from_resource(uri)
            
            if success:
                logger.debug(f"Unsubscribed from resource {uri}")
            else:
                logger.warning(f"Failed to unsubscribe from resource {uri}")
                
        except Exception as e:
            logger.error(f"Error unsubscribing from resource {uri}: {e}")
    
    return {
        "list_resources": list_resources,
        "read_resource": read_resource,
        "subscribe_resource": subscribe_resource,
        "unsubscribe_resource": unsubscribe_resource
    } 