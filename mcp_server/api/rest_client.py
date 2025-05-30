import logging
import json
import requests
from typing import Dict, Any, Optional, Union, List
from mcp import types
from mcp_server.core.mcp_setup import mcp, get_service_context
from mcp_server.config.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RestApiClient:
    """Client for making REST API requests."""

    def __init__(self, base_url: str, headers: Optional[Dict[str, str]] = None):
        """
        Initialize the REST API client.

        Args:
            base_url: Base URL for API requests
            headers: Optional headers to include in all requests
        """
        self.base_url = base_url.rstrip("/")
        self.headers = headers or {}
        self.session = requests.Session()
        
        default_headers = settings.API_DEFAULT_HEADERS.copy()
        default_headers.update(self.headers)
        self.session.headers.update(default_headers)
        
        self.session.timeout = settings.API_REQUEST_TIMEOUT

    def get(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> requests.Response:
        """
        Make a GET request.

        Args:
            endpoint: API endpoint
            params: Optional query parameters

        Returns:
            Response object
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        logger.info(f"Making GET request to {url}")
        
        return self.session.get(
            url, 
            params=params,
            timeout=settings.API_REQUEST_TIMEOUT
        )

    def post(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> requests.Response:
        """
        Make a POST request.

        Args:
            endpoint: API endpoint
            data: Optional form data
            json_data: Optional JSON data

        Returns:
            Response object
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        logger.info(f"Making POST request to {url}")
        
        return self.session.post(
            url, 
            data=data, 
            json=json_data,
            timeout=settings.API_REQUEST_TIMEOUT
        )

    def put(
        self,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
    ) -> requests.Response:
        """
        Make a PUT request.

        Args:
            endpoint: API endpoint
            data: Optional form data
            json_data: Optional JSON data

        Returns:
            Response object
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        logger.info(f"Making PUT request to {url}")
        
        return self.session.put(
            url, 
            data=data, 
            json=json_data,
            timeout=settings.API_REQUEST_TIMEOUT
        )

    def delete(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None
    ) -> requests.Response:
        """
        Make a DELETE request.

        Args:
            endpoint: API endpoint
            params: Optional query parameters

        Returns:
            Response object
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        logger.info(f"Making DELETE request to {url}")
        
        return self.session.delete(
            url, 
            params=params,
            timeout=settings.API_REQUEST_TIMEOUT
        )


@mcp.tool(name="api_init", description="Initialize the API client with a base URL.")
async def api_init(base_url: str, headers: Optional[Dict[str, str]] = None) -> List[types.TextContent]:
    """
    Initialize the API client with a base URL.

    Args:
        base_url: Base URL for API requests
        headers: Optional headers to include in all requests

    Returns:
        List of TextContent với confirmation message
    """
    try:
        if not settings.validate_url(base_url):
            return [types.TextContent(
                type="text",
                text=f"Error: URL exceeds maximum length of {settings.MAX_URL_LENGTH} characters"
            )]

        context = await get_service_context()
        context.api_client = RestApiClient(base_url, headers)
        
        return [types.TextContent(
            type="text",
            text=f"API client initialized successfully with base URL: {base_url}"
        )]
    except Exception as e:
        error_msg = f"Failed to initialize API client: {str(e)}"
        logger.error(error_msg)
        return [types.TextContent(
            type="text",
            text=error_msg
        )]


@mcp.tool(name="api_get", description="Make a GET request to an API endpoint.")
async def api_get(
    endpoint: str,
    params: Optional[Dict[str, Any]] = None,
    base_url: Optional[str] = None,
) -> List[types.TextContent]:
    """
    Make a GET request to an API endpoint.

    Args:
        endpoint: API endpoint
        params: Optional query parameters
        base_url: Optional base URL (overrides the initialized client base URL)

    Returns:
        List of TextContent với response from the API
    """
    try:
        context = await get_service_context()
        
        if base_url:
            if not settings.validate_url(base_url):
                return [types.TextContent(
                    type="text",
                    text=f"Error: URL exceeds maximum length of {settings.MAX_URL_LENGTH} characters"
                )]
            temp_client = RestApiClient(base_url)
            response = temp_client.get(endpoint, params)
        else:
            if not context.api_client:
                return [types.TextContent(
                    type="text",
                    text="Error: API client not initialized. Use api_init first."
                )]
            response = context.api_client.get(endpoint, params)

        response_text = f"Status Code: {response.status_code}\n"
        response_text += f"Headers: {dict(response.headers)}\n\n"
        
        try:
            response_json = response.json()
            response_text += f"Response Body:\n{json.dumps(response_json, indent=2)}"
        except ValueError:
            response_text += f"Response Body:\n{response.text}"
            
        return [types.TextContent(
            type="text",
            text=response_text
        )]
        
    except Exception as e:
        error_msg = f"API request failed: {str(e)}"
        logger.error(error_msg)
        return [types.TextContent(
            type="text",
            text=error_msg
        )]


@mcp.tool(name="api_post", description="Make a POST request to an API endpoint.")
async def api_post(
    endpoint: str,
    json_data: Optional[Dict[str, Any]] = None,
    data: Optional[Dict[str, Any]] = None,
    base_url: Optional[str] = None,
) -> List[types.TextContent]:
    """
    Make a POST request to an API endpoint.

    Args:
        endpoint: API endpoint
        json_data: Optional JSON data
        data: Optional form data
        base_url: Optional base URL (overrides the initialized client base URL)

    Returns:
        List of TextContent với response from the API
    """
    try:
        context = await get_service_context()
        
        if base_url:
            if not settings.validate_url(base_url):
                return [types.TextContent(
                    type="text",
                    text=f"Error: URL exceeds maximum length of {settings.MAX_URL_LENGTH} characters"
                )]
            temp_client = RestApiClient(base_url)
            response = temp_client.post(endpoint, data, json_data)
        else:
            if not context.api_client:
                return [types.TextContent(
                    type="text",
                    text="Error: API client not initialized. Use api_init first."
                )]
            response = context.api_client.post(endpoint, data, json_data)

        response_text = f"Status Code: {response.status_code}\n"
        response_text += f"Headers: {dict(response.headers)}\n\n"
        
        try:
            response_json = response.json()
            response_text += f"Response Body:\n{json.dumps(response_json, indent=2)}"
        except ValueError:
            response_text += f"Response Body:\n{response.text}"
            
        return [types.TextContent(
            type="text",
            text=response_text
        )]
        
    except Exception as e:
        error_msg = f"API request failed: {str(e)}"
        logger.error(error_msg)
        return [types.TextContent(
            type="text",
            text=error_msg
        )]


@mcp.tool(name="api_put", description="Make a PUT request to an API endpoint.")
async def api_put(
    endpoint: str,
    json_data: Optional[Dict[str, Any]] = None,
    data: Optional[Dict[str, Any]] = None,
    base_url: Optional[str] = None,
) -> List[types.TextContent]:
    """
    Make a PUT request to an API endpoint.

    Args:
        endpoint: API endpoint
        json_data: Optional JSON data
        data: Optional form data
        base_url: Optional base URL (overrides the initialized client base URL)

    Returns:
        List of TextContent với response from the API
    """
    try:
        context = await get_service_context()
        
        if base_url:
            if not settings.validate_url(base_url):
                return [types.TextContent(
                    type="text",
                    text=f"Error: URL exceeds maximum length of {settings.MAX_URL_LENGTH} characters"
                )]
            temp_client = RestApiClient(base_url)
            response = temp_client.put(endpoint, data, json_data)
        else:
            if not context.api_client:
                return [types.TextContent(
                    type="text",
                    text="Error: API client not initialized. Use api_init first."
                )]
            response = context.api_client.put(endpoint, data, json_data)

        response_text = f"Status Code: {response.status_code}\n"
        response_text += f"Headers: {dict(response.headers)}\n\n"
        
        try:
            response_json = response.json()
            response_text += f"Response Body:\n{json.dumps(response_json, indent=2)}"
        except ValueError:
            response_text += f"Response Body:\n{response.text}"
            
        return [types.TextContent(
            type="text",
            text=response_text
        )]
        
    except Exception as e:
        error_msg = f"API request failed: {str(e)}"
        logger.error(error_msg)
        return [types.TextContent(
            type="text",
            text=error_msg
        )]


@mcp.tool(name="api_delete", description="Make a DELETE request to an API endpoint.")
async def api_delete(
    endpoint: str,
    params: Optional[Dict[str, Any]] = None,
    base_url: Optional[str] = None,
) -> List[types.TextContent]:
    """
    Make a DELETE request to an API endpoint.

    Args:
        endpoint: API endpoint
        params: Optional query parameters
        base_url: Optional base URL (overrides the initialized client base URL)

    Returns:
        List of TextContent với response from the API
    """
    try:
        context = await get_service_context()
        
        if base_url:
            if not settings.validate_url(base_url):
                return [types.TextContent(
                    type="text",
                    text=f"Error: URL exceeds maximum length of {settings.MAX_URL_LENGTH} characters"
                )]
            temp_client = RestApiClient(base_url)
            response = temp_client.delete(endpoint, params)
        else:
            if not context.api_client:
                return [types.TextContent(
                    type="text",
                    text="Error: API client not initialized. Use api_init first."
                )]
            response = context.api_client.delete(endpoint, params)

        response_text = f"Status Code: {response.status_code}\n"
        response_text += f"Headers: {dict(response.headers)}\n\n"
        
        try:
            response_json = response.json()
            response_text += f"Response Body:\n{json.dumps(response_json, indent=2)}"
        except ValueError:
            response_text += f"Response Body:\n{response.text}"
            
        return [types.TextContent(
            type="text",
            text=response_text
        )]
        
    except Exception as e:
        error_msg = f"API request failed: {str(e)}"
        logger.error(error_msg)
        return [types.TextContent(
            type="text",
            text=error_msg
        )]
