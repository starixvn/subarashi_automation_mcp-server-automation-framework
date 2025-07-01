
import asyncio
import logging
import mimetypes
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional, Dict, Any, TYPE_CHECKING
from urllib.parse import urlparse, unquote

from .models import (
    Resource, 
    ResourceContent, 
    TextResourceContent, 
    BlobResourceContent,
    guess_mime_type
)

if TYPE_CHECKING:
    from context import ServerContext

logger = logging.getLogger(__name__)


class ResourceProvider(ABC):
    
    def __init__(self, scheme: str):
        self.scheme = scheme
        self._subscribers: Dict[str, List[Any]] = {}
        self._file_watchers: Dict[str, Any] = {}
    
    @abstractmethod
    async def list_resources(self) -> List[Resource]:
        pass
    
    @abstractmethod
    async def read_resource(self, uri: str) -> List[ResourceContent]:
        pass
    
    async def subscribe_to_resource(self, uri: str, callback) -> bool:
        if uri not in self._subscribers:
            self._subscribers[uri] = []
        self._subscribers[uri].append(callback)
        return True
    
    async def unsubscribe_from_resource(self, uri: str) -> bool:
        if uri in self._subscribers:
            del self._subscribers[uri]
        return True


class FileSystemResourceProvider(ResourceProvider):
    
    def __init__(
        self, 
        root_paths: Optional[List[str]] = None,
        allowed_extensions: Optional[List[str]] = None,
        max_file_size: int = 10 * 1024 * 1024  # 10MB default
    ):
        super().__init__("file")
        
        self.root_paths = [Path(path) for path in (root_paths or [os.getcwd()])]
        self.allowed_extensions = set(allowed_extensions or [
            '.txt', '.md', '.json', '.yaml', '.yml', '.xml', '.csv',
            '.log', '.py', '.js', '.ts', '.html', '.css', '.sql',
            '.toml', '.ini', '.cfg', '.conf'
        ])
        self.max_file_size = max_file_size
        
        logger.info(f"FileSystemResourceProvider initialized with {len(self.root_paths)} root paths")
    
    async def list_resources(self) -> List[Resource]:
        resources = []
        
        for root_path in self.root_paths:
            if not root_path.exists():
                logger.warning(f"Root path does not exist: {root_path}")
                continue
                
            try:
                for file_path in root_path.rglob("*"):
                    if file_path.is_file():
                        try:
                            file_size = file_path.stat().st_size
                            if file_size > self.max_file_size:
                                continue
                        except (OSError, IOError):
                            continue
                        
                        if self.allowed_extensions and file_path.suffix.lower() not in self.allowed_extensions:
                            continue
                        
                        try:
                            relative_path = file_path.relative_to(root_path).as_posix()
                            uri = f"file:///{relative_path}"
                            
                            resource = Resource(
                                uri=uri,
                                name=file_path.name,
                                description=f"File: {file_path}",
                                mime_type=guess_mime_type(file_path.name),
                                size=file_size
                            )
                            resources.append(resource)
                            
                        except (ValueError, OSError) as e:
                            logger.debug(f"Skipping file {file_path}: {e}")
                            continue
                            
            except (OSError, PermissionError) as e:
                logger.warning(f"Error accessing root path {root_path}: {e}")
                continue
        
        logger.debug(f"Listed {len(resources)} file resources")
        return resources
    
    async def read_resource(self, uri: str) -> List[ResourceContent]:
        try:
            parsed = urlparse(uri)
            if parsed.scheme != "file":
                raise ValueError(f"Unsupported URI scheme: {parsed.scheme}")
            
            relative_path = unquote(parsed.path).lstrip('/')
            if not relative_path and parsed.netloc:
                relative_path = parsed.netloc
            
            file_path = None
            for root_path in self.root_paths:
                candidate = root_path / relative_path
                if candidate.exists() and candidate.is_file():
                    file_path = candidate
                    break
            
            if not file_path:
                raise FileNotFoundError(f"File not found: {relative_path}")
            
            file_size = file_path.stat().st_size
            if file_size > self.max_file_size:
                raise ValueError(f"File too large: {file_size} bytes (max: {self.max_file_size})")
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                return [TextResourceContent(
                    uri=uri,
                    mime_type="text/plain",
                    text=content
                )]
                
            except UnicodeDecodeError:
                with open(file_path, 'rb') as f:
                    content = f.read()
                return [BlobResourceContent.from_bytes(
                    uri=uri,
                    data=content,
                    mime_type=mimetypes.guess_type(str(file_path))[0]
                )]
                
        except Exception as e:
            logger.error(f"Error reading resource {uri}: {e}")
            raise


class BrowserResourceProvider(ResourceProvider):
    
    def __init__(self, context: "ServerContext"):
        super().__init__("browser")
        self.context = context
    
    async def list_resources(self) -> List[Resource]:
        resources = []
        
        resources.append(Resource(
            uri="browser://current-page",
            name="Current Page",
            description="Current browser page content",
            mime_type="text/html"
        ))
        
        try:
            tabs = self.context.tabs()
            for i, tab in enumerate(tabs):
                uri = f"browser://tab/{i}"
                title = await tab.title() if hasattr(tab, 'title') else f"Tab {i+1}"
                
                resources.append(Resource(
                    uri=uri,
                    name=f"Tab {i+1}: {title}",
                    description=f"Content of browser tab {i+1}",
                    mime_type="text/html"
                ))
        except Exception as e:
            logger.debug(f"Error listing tabs: {e}")
        
        return resources
    
    async def read_resource(self, uri: str) -> List[ResourceContent]:
        """Read browser resource content."""
        try:
            if uri == "browser://current-page":
                try:
                    current_tab = self.context.current_tab_or_die()
                    content = await current_tab.page.content()
                    return [TextResourceContent(
                        uri=uri,
                        mime_type="text/html",
                        text=content
                    )]
                except Exception as e:
                    return [TextResourceContent(
                        uri=uri,
                        mime_type="text/plain",
                        text=f"No active browser page: {str(e)}"
                    )]
            
            elif uri.startswith("browser://tab/"):
                tab_index = int(uri.split("/")[-1])
                tabs = self.context.tabs()
                
                if 0 <= tab_index < len(tabs):
                    tab = tabs[tab_index]
                    content = await tab.page.content()
                    return [TextResourceContent(
                        uri=uri,
                        mime_type="text/html",
                        text=content
                    )]
                else:
                    raise ValueError(f"Tab index {tab_index} out of range")
            
            else:
                raise ValueError(f"Unknown browser resource: {uri}")
                
        except Exception as e:
            logger.error(f"Error reading browser resource {uri}: {e}")
            raise


class DatabaseResourceProvider(ResourceProvider):
    
    def __init__(self):
        super().__init__("db")
        self._connections: Dict[str, Any] = {}
    
    async def list_resources(self) -> List[Resource]:
        resources = []
        
        for conn_name in self._connections:
            resources.append(Resource(
                uri=f"db://{conn_name}/info",
                name=f"Database {conn_name} Info",
                description=f"Connection info for database {conn_name}",
                mime_type="application/json"
            ))
        
        return resources
    
    async def read_resource(self, uri: str) -> List[ResourceContent]:
        try:
            parsed = urlparse(uri)
            if parsed.scheme != "db":
                raise ValueError(f"Unsupported URI scheme: {parsed.scheme}")
            
            conn_name = parsed.netloc
            if conn_name not in self._connections:
                raise ValueError(f"Database connection '{conn_name}' not found")
            
            import json
            info = {
                "connection_name": conn_name,
                "status": "connected",
                "available_tables": []  # Could be populated with actual table info
            }
            
            return [TextResourceContent(
                uri=uri,
                mime_type="application/json",
                text=json.dumps(info, indent=2)
            )]
            
        except Exception as e:
            logger.error(f"Error reading database resource {uri}: {e}")
            raise
    
    def add_connection(self, name: str, connection: Any):
        self._connections[name] = connection
        logger.info(f"Added database connection: {name}")
    
    def remove_connection(self, name: str):
        if name in self._connections:
            del self._connections[name]
            logger.info(f"Removed database connection: {name}") 