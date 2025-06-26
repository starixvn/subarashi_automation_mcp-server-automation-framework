"""
MCP Resources Module

Provides resource access and management for MCP server.
"""

from .models import Resource, ResourceContent, TextResourceContent, BlobResourceContent
from .providers import ResourceProvider, FileSystemResourceProvider, BrowserResourceProvider, DatabaseResourceProvider
from .registry import ResourceRegistry, resource_registry
from .handlers import get_resources_handlers

__all__ = [
    "Resource",
    "ResourceContent", 
    "TextResourceContent",
    "BlobResourceContent",
    "ResourceProvider",
    "FileSystemResourceProvider", 
    "BrowserResourceProvider",
    "DatabaseResourceProvider",
    "ResourceRegistry",
    "resource_registry",
    "get_resources_handlers"
] 