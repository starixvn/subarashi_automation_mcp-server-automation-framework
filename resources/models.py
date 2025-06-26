"""
MCP Resources Models

Models for MCP resource system following the exact MCP protocol specification.
"""

import base64
import mimetypes
from typing import Optional, Union
from pydantic import BaseModel, Field
from pydantic.networks import AnyUrl, UrlConstraints
from typing_extensions import Annotated

from mcp.types import (
    Resource as MCPResource,
    ResourceContents as MCPResourceContents,
    TextResourceContents as MCPTextResourceContents,
    BlobResourceContents as MCPBlobResourceContents,
    ReadResourceResult
)


class ResourceContent(BaseModel):
    """Base class for resource content."""
    
    uri: Annotated[AnyUrl, UrlConstraints(host_required=False)]
    """The URI of this resource."""
    
    mime_type: Optional[str] = None
    """The MIME type of this resource, if known."""
    
    def to_mcp_contents(self) -> MCPResourceContents:
        """Convert to MCP protocol format. Must be implemented by subclasses."""
        raise NotImplementedError("Subclasses must implement to_mcp_contents")


class TextResourceContent(ResourceContent):
    """Text content of a resource."""
    
    text: str
    """The text content of the resource."""
    
    def to_mcp_contents(self) -> MCPTextResourceContents:
        """Convert to MCP protocol format."""
        return MCPTextResourceContents(
            uri=self.uri,
            mimeType=self.mime_type or "text/plain",
            text=self.text
        )


class BlobResourceContent(ResourceContent):
    """Binary content of a resource."""
    
    blob: str
    """A base64-encoded string representing the binary data."""
    
    def to_mcp_contents(self) -> MCPBlobResourceContents:
        """Convert to MCP protocol format."""
        return MCPBlobResourceContents(
            uri=self.uri,
            mimeType=self.mime_type or "application/octet-stream",
            blob=self.blob
        )
    
    @classmethod
    def from_bytes(
        cls, 
        uri: Union[str, AnyUrl], 
        data: bytes, 
        mime_type: Optional[str] = None
    ) -> "BlobResourceContent":
        """Create BlobResourceContent from raw bytes."""
        if isinstance(uri, str):
            uri = AnyUrl(uri)
        
        return cls(
            uri=uri,
            blob=base64.b64encode(data).decode('utf-8'),
            mime_type=mime_type
        )


class ResourceTemplate(BaseModel):
    """A template description for resources available on the server."""
    
    uri_template: str
    """A URI template (according to RFC 6570) that can be used to construct resource URIs."""
    
    name: str
    """A human-readable name for the type of resource this template refers to."""
    
    description: Optional[str] = None
    """A description of what this template is for."""
    
    mime_type: Optional[str] = None
    """The MIME type for all resources that match this template."""


class Resource(BaseModel):
    """A known resource that the server is capable of reading."""
    
    uri: Annotated[AnyUrl, UrlConstraints(host_required=False)]
    """The URI of this resource."""
    
    name: str
    """A human-readable name for this resource."""
    
    description: Optional[str] = None
    """A description of what this resource represents."""
    
    mime_type: Optional[str] = None
    """The MIME type of this resource, if known."""
    
    size: Optional[int] = None
    """The size of the raw resource content in bytes, if known."""
    
    def to_mcp_resource(self) -> MCPResource:
        """Convert to MCP protocol format."""
        return MCPResource(
            uri=self.uri,
            name=self.name,
            description=self.description,
            mimeType=self.mime_type,
            size=self.size
        )


def create_read_resource_result(contents: list[ResourceContent]) -> ReadResourceResult:
    """Create a ReadResourceResult from resource contents."""
    mcp_contents = [content.to_mcp_contents() for content in contents]
    return ReadResourceResult(contents=mcp_contents)


def guess_mime_type(filename: str) -> str:
    """Guess MIME type from filename."""
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type or "application/octet-stream" 