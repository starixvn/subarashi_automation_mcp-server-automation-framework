import mimetypes
from mcp.server.fastmcp.resources import (
    Resource,
    TextResource,
    BinaryResource,
    FileResource,
    FunctionResource,
    HttpResource,
    DirectoryResource,
    ResourceTemplate,
)

__all__ = [
    "Resource",
    "TextResource",
    "BinaryResource",
    "FileResource",
    "FunctionResource",
    "HttpResource",
    "DirectoryResource",
    "ResourceTemplate",
    "guess_mime_type",
]


def guess_mime_type(filename: str) -> str:
    """Guess MIME type from filename."""
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type or "application/octet-stream"
