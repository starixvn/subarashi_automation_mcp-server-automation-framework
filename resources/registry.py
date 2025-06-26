"""
MCP Resources Registry

Registry for managing resource providers following MCP protocol.
"""

import logging
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse

from .models import Resource, ResourceContent, create_read_resource_result
from .providers import ResourceProvider

logger = logging.getLogger(__name__)


class ResourceRegistry:
    """Registry for managing MCP resource providers."""
    
    def __init__(self):
        self._providers: Dict[str, ResourceProvider] = {}
    
    def register_provider(self, scheme: str, provider: ResourceProvider) -> None:
        """Register a resource provider for a URI scheme."""
        if scheme in self._providers:
            # Check if it's the same provider instance
            if self._providers[scheme] is provider:
                logger.debug(f"Provider for scheme '{scheme}' already registered with same instance")
                return
            logger.warning(f"Provider for scheme '{scheme}' already registered, replacing")
        
        self._providers[scheme] = provider
        logger.debug(f"Registered provider for scheme: {scheme}")
    
    def get_provider(self, scheme: str) -> Optional[ResourceProvider]:
        """Get a provider by URI scheme."""
        return self._providers.get(scheme)
    
    def get_providers(self) -> Dict[str, ResourceProvider]:
        """Get all registered providers."""
        return self._providers.copy()
    
    def unregister_provider(self, scheme: str) -> bool:
        """Unregister a provider by scheme."""
        if scheme in self._providers:
            del self._providers[scheme]
            logger.debug(f"Unregistered provider for scheme: {scheme}")
            return True
        return False
    
    def clear(self) -> None:
        """Clear all registered providers."""
        self._providers.clear()
        logger.debug("Cleared all providers")
    
    async def list_resources(self) -> List[Resource]:
        """List all resources from all providers."""
        all_resources = []
        
        for scheme, provider in self._providers.items():
            try:
                resources = await provider.list_resources()
                all_resources.extend(resources)
                logger.debug(f"Got {len(resources)} resources from {scheme} provider")
                
            except Exception as e:
                logger.error(f"Error listing resources from {scheme} provider: {e}")
                continue
        
        logger.debug(f"Total resources across all providers: {len(all_resources)}")
        return all_resources
    
    async def read_resource(self, uri: str) -> Any:
        """Read a resource by URI using the appropriate provider."""
        try:
            # Parse URI to get scheme
            parsed = urlparse(uri)
            scheme = parsed.scheme
            
            if not scheme:
                raise ValueError(f"Invalid URI (no scheme): {uri}")
            
            # Get provider for scheme
            provider = self.get_provider(scheme)
            if not provider:
                raise ValueError(f"No provider registered for scheme: {scheme}")
            
            # Read resource content
            contents = await provider.read_resource(uri)
            
            # Create MCP result
            result = create_read_resource_result(contents)
            
            logger.debug(f"Read resource {uri} with {len(contents)} content items")
            return result
            
        except Exception as e:
            logger.error(f"Error reading resource {uri}: {e}")
            raise
    
    async def subscribe_to_resource(self, uri: str, callback) -> bool:
        """Subscribe to resource updates."""
        try:
            parsed = urlparse(uri)
            provider = self.get_provider(parsed.scheme)
            
            if not provider:
                raise ValueError(f"No provider for scheme: {parsed.scheme}")
            
            return await provider.subscribe_to_resource(uri, callback)
            
        except Exception as e:
            logger.error(f"Error subscribing to resource {uri}: {e}")
            return False
    
    async def unsubscribe_from_resource(self, uri: str) -> bool:
        """Unsubscribe from resource updates."""
        try:
            parsed = urlparse(uri)
            provider = self.get_provider(parsed.scheme)
            
            if not provider:
                raise ValueError(f"No provider for scheme: {parsed.scheme}")
            
            return await provider.unsubscribe_from_resource(uri)
            
        except Exception as e:
            logger.error(f"Error unsubscribing from resource {uri}: {e}")
            return False


# Global resource registry instance
resource_registry = ResourceRegistry() 