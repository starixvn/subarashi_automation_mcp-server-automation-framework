"""
REST API client functionality for MCP Tools.
"""

import logging
import json
import requests
from typing import Dict, Any, Optional, Union, List

from mcp_tools.server.core.mcp_setup import mcp

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
        self.session.headers.update(self.headers)

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
        return self.session.get(url, params=params)

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
        return self.session.post(url, data=data, json=json_data)

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
        return self.session.put(url, data=data, json=json_data)

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
        return self.session.delete(url, params=params)


# Shared client instance for API requests
api_client = None


@mcp.tool(name="API-Init", description="Initialize the API client with a base URL.")
async def api_init(base_url: str, headers: Optional[Dict[str, str]] = None) -> str:
    """
    Initialize the API client with a base URL.

    Args:
        base_url: Base URL for API requests
        headers: Optional headers to include in all requests

    Returns:
        Confirmation message
    """
    global api_client
    try:
        api_client = RestApiClient(base_url, headers)
        return f"API client initialized with base URL: {base_url}"
    except Exception as e:
        error_msg = f"Failed to initialize API client: {str(e)}"
        logger.error(error_msg)
        return error_msg


@mcp.tool(name="API-GET", description="Make a GET request to an API endpoint.")
async def api_get(
    endpoint: str,
    params: Optional[Dict[str, Any]] = None,
    base_url: Optional[str] = None,
) -> str:
    """
    Make a GET request to an API endpoint.

    Args:
        endpoint: API endpoint
        params: Optional query parameters
        base_url: Optional base URL (overrides the initialized client base URL)

    Returns:
        Response from the API as a JSON string
    """
    global api_client
    try:
        if base_url:
            temp_client = RestApiClient(base_url)
            response = temp_client.get(endpoint, params)
        else:
            if not api_client:
                return "Error: API client not initialized. Use API-Init first."
            response = api_client.get(endpoint, params)

        # Format response for better readability
        try:
            return json.dumps(response.json(), indent=2)
        except ValueError:
            return response.text
    except Exception as e:
        error_msg = f"API request failed: {str(e)}"
        logger.error(error_msg)
        return error_msg


@mcp.tool(name="API-POST", description="Make a POST request to an API endpoint.")
async def api_post(
    endpoint: str,
    json_data: Optional[Dict[str, Any]] = None,
    data: Optional[Dict[str, Any]] = None,
    base_url: Optional[str] = None,
) -> str:
    """
    Make a POST request to an API endpoint.

    Args:
        endpoint: API endpoint
        json_data: Optional JSON data
        data: Optional form data
        base_url: Optional base URL (overrides the initialized client base URL)

    Returns:
        Response from the API as a JSON string
    """
    global api_client
    try:
        if base_url:
            temp_client = RestApiClient(base_url)
            response = temp_client.post(endpoint, data, json_data)
        else:
            if not api_client:
                return "Error: API client not initialized. Use API-Init first."
            response = api_client.post(endpoint, data, json_data)

        # Format response for better readability
        try:
            return json.dumps(response.json(), indent=2)
        except ValueError:
            return response.text
    except Exception as e:
        error_msg = f"API request failed: {str(e)}"
        logger.error(error_msg)
        return error_msg


@mcp.tool(name="API-PUT", description="Make a PUT request to an API endpoint.")
async def api_put(
    endpoint: str,
    json_data: Optional[Dict[str, Any]] = None,
    data: Optional[Dict[str, Any]] = None,
    base_url: Optional[str] = None,
) -> str:
    """
    Make a PUT request to an API endpoint.

    Args:
        endpoint: API endpoint
        json_data: Optional JSON data
        data: Optional form data
        base_url: Optional base URL (overrides the initialized client base URL)

    Returns:
        Response from the API as a JSON string
    """
    global api_client
    try:
        if base_url:
            temp_client = RestApiClient(base_url)
            response = temp_client.put(endpoint, data, json_data)
        else:
            if not api_client:
                return "Error: API client not initialized. Use API-Init first."
            response = api_client.put(endpoint, data, json_data)

        # Format response for better readability
        try:
            return json.dumps(response.json(), indent=2)
        except ValueError:
            return response.text
    except Exception as e:
        error_msg = f"API request failed: {str(e)}"
        logger.error(error_msg)
        return error_msg


@mcp.tool(name="API-DELETE", description="Make a DELETE request to an API endpoint.")
async def api_delete(
    endpoint: str,
    params: Optional[Dict[str, Any]] = None,
    base_url: Optional[str] = None,
) -> str:
    """
    Make a DELETE request to an API endpoint.

    Args:
        endpoint: API endpoint
        params: Optional query parameters
        base_url: Optional base URL (overrides the initialized client base URL)

    Returns:
        Response from the API as a JSON string
    """
    global api_client
    try:
        if base_url:
            temp_client = RestApiClient(base_url)
            response = temp_client.delete(endpoint, params)
        else:
            if not api_client:
                return "Error: API client not initialized. Use API-Init first."
            response = api_client.delete(endpoint, params)

        # Format response for better readability
        try:
            return json.dumps(response.json(), indent=2)
        except ValueError:
            return response.text
    except Exception as e:
        error_msg = f"API request failed: {str(e)}"
        logger.error(error_msg)
        return error_msg
