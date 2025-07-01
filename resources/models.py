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
    
    uri: Annotated[AnyUrl, UrlConstraints(host_required=False)]
    mime_type: Optional[str] = None
    
    def to_mcp_contents(self) -> MCPResourceContents:
        raise NotImplementedError("Subclasses must implement to_mcp_contents")


class TextResourceContent(ResourceContent):
    
    text: str
    
    def to_mcp_contents(self) -> MCPTextResourceContents:
        return MCPTextResourceContents(
            uri=self.uri,
            mimeType=self.mime_type or "text/plain",
            text=self.text
        )


class BlobResourceContent(ResourceContent):
    
    blob: str
    
    def to_mcp_contents(self) -> MCPBlobResourceContents:
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
        if isinstance(uri, str):
            uri = AnyUrl(uri)
        
        return cls(
            uri=uri,
            blob=base64.b64encode(data).decode('utf-8'),
            mime_type=mime_type
        )


class ResourceTemplate(BaseModel):
    
    uri_template: str
    name: str
    description: Optional[str] = None
    mime_type: Optional[str] = None


class Resource(BaseModel):
    
    uri: Annotated[AnyUrl, UrlConstraints(host_required=False)]
    name: str
    description: Optional[str] = None
    mime_type: Optional[str] = None
    size: Optional[int] = None
    
    def to_mcp_resource(self) -> MCPResource:
        return MCPResource(
            uri=self.uri,
            name=self.name,
            description=self.description,
            mimeType=self.mime_type,
            size=self.size
        )


def create_read_resource_result(contents: list[ResourceContent]) -> ReadResourceResult:
    mcp_contents = [content.to_mcp_contents() for content in contents]
    return ReadResourceResult(contents=mcp_contents)


def guess_mime_type(filename: str) -> str:
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type or "application/octet-stream" 