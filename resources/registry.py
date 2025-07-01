
import logging
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse

from .models import Resource, ResourceContent, create_read_resource_result
from .providers import ResourceProvider

logger = logging.getLogger(__name__)


class ResourceRegistry:
    
    def __init__(self):
        self._providers: Dict[str, ResourceProvider] = {}
    
    def register_provider(self, scheme: str, provider: ResourceProvider) -> None:
        if scheme in self._providers:
            if self._providers[scheme] is provider:
                logger.debug(f"Provider for scheme '{scheme}' already registered with same instance")
                return
            logger.warning(f"Provider for scheme '{scheme}' already registered, replacing")
        
        self._providers[scheme] = provider
        logger.debug(f"Registered provider for scheme: {scheme}")
    
    def get_provider(self, scheme: str) -> Optional[ResourceProvider]:
        return self._providers.get(scheme)
    
    def get_providers(self) -> Dict[str, ResourceProvider]:
        return self._providers.copy()
    
    def unregister_provider(self, scheme: str) -> bool:
        if scheme in self._providers:
            del self._providers[scheme]
            logger.debug(f"Unregistered provider for scheme: {scheme}")
            return True
        return False
    
    def clear(self) -> None:
        self._providers.clear()
        logger.debug("Cleared all providers")
    
    async def list_resources(self) -> List[Resource]:
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
        try:
            parsed = urlparse(uri)
            scheme = parsed.scheme
            
            if not scheme:
                raise ValueError(f"Invalid URI (no scheme): {uri}")
            
            provider = self.get_provider(scheme)
            if not provider:
                raise ValueError(f"No provider registered for scheme: {scheme}")
            
            contents = await provider.read_resource(uri)
            
            result = create_read_resource_result(contents)
            
            logger.debug(f"Read resource {uri} with {len(contents)} content items")
            return result
            
        except Exception as e:
            logger.error(f"Error reading resource {uri}: {e}")
            raise
    
    async def subscribe_to_resource(self, uri: str, callback) -> bool:
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
        try:
            parsed = urlparse(uri)
            provider = self.get_provider(parsed.scheme)
            
            if not provider:
                raise ValueError(f"No provider for scheme: {parsed.scheme}")
            
            return await provider.unsubscribe_from_resource(uri)
            
        except Exception as e:
            logger.error(f"Error unsubscribing from resource {uri}: {e}")
            return False


resource_registry = ResourceRegistry() 