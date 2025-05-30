import logging
import json
import base64
import time
import requests
from typing import Dict, Any, Optional, Union, List

from mcp import types
from mcp_server.core.mcp_setup import mcp, get_service_context
from mcp_server.api.rest_client import RestApiClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@mcp.tool(
    name="api_basic_auth", description="Set up Basic Authentication for API requests."
)
async def api_basic_auth(username: str, password: str) -> List[types.TextContent]:
    """
    Set up Basic Authentication for API requests.

    Args:
        username: Username for Basic Authentication
        password: Password for Basic Authentication

    Returns:
        List of TextContent với confirmation message
    """
    try:
        context = await get_service_context()
        
        if not context.api_client:
            return [types.TextContent(
                type="text",
                text="Error: API client not initialized. Use api_init first."
            )]

        auth_string = f"{username}:{password}"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        context.api_client.session.headers.update({"Authorization": f"Basic {encoded_auth}"})
        
        return [types.TextContent(
            type="text",
            text="Basic Authentication set up successfully"
        )]
        
    except Exception as e:
        error_msg = f"Failed to set up Basic Authentication: {str(e)}"
        logger.error(error_msg)
        return [types.TextContent(
            type="text",
            text=error_msg
        )]


@mcp.tool(
    name="api_bearer_token",
    description="Set up Bearer Token Authentication for API requests.",
)
async def api_bearer_token(token: str) -> List[types.TextContent]:
    """
    Set up Bearer Token Authentication for API requests.

    Args:
        token: Bearer token for Authentication

    Returns:
        List of TextContent với confirmation message
    """
    try:
        context = await get_service_context()
        
        if not context.api_client:
            return [types.TextContent(
                type="text",
                text="Error: API client not initialized. Use api_init first."
            )]

        context.api_client.session.headers.update({"Authorization": f"Bearer {token}"})
        
        return [types.TextContent(
            type="text",
            text="Bearer Token Authentication set up successfully"
        )]
        
    except Exception as e:
        error_msg = f"Failed to set up Bearer Token Authentication: {str(e)}"
        logger.error(error_msg)
        return [types.TextContent(
            type="text",
            text=error_msg
        )]


@mcp.tool(
    name="api_oauth2_client_credentials",
    description="Get OAuth2 token using client credentials flow and set it for API requests.",
)
async def api_oauth2_client_credentials(
    token_url: str, client_id: str, client_secret: str, scope: Optional[str] = None
) -> List[types.TextContent]:
    """
    Get OAuth2 token using client credentials flow and set it for API requests.

    Args:
        token_url: OAuth2 token endpoint URL
        client_id: OAuth2 client ID
        client_secret: OAuth2 client secret
        scope: Optional OAuth2 scope

    Returns:
        List of TextContent với confirmation message with token details
    """
    try:
        context = await get_service_context()
        
        if not context.api_client:
            return [types.TextContent(
                type="text",
                text="Error: API client not initialized. Use api_init first."
            )]

        data = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
        }

        if scope:
            data["scope"] = scope

        temp_client = RestApiClient("")
        response = temp_client.post(token_url, data=data)

        if response.status_code != 200:
            return [types.TextContent(
                type="text",
                text=f"Failed to get OAuth2 token: {response.text}"
            )]

        token_data = response.json()

        if "expires_in" in token_data:
            token_data["expires_at"] = time.time() + token_data["expires_in"]

        token = token_data.get("access_token")
        context.api_client.session.headers.update({"Authorization": f"Bearer {token}"})

        return [types.TextContent(
            type="text",
            text=f"OAuth2 token acquired successfully. Expires in {token_data.get('expires_in', 'unknown')} seconds."
        )]
        
    except Exception as e:
        error_msg = f"Failed to get OAuth2 token: {str(e)}"
        logger.error(error_msg)
        return [types.TextContent(
            type="text",
            text=error_msg
        )]


@mcp.tool(
    name="api_clear_auth", description="Clear authentication settings from API client."
)
async def api_clear_auth() -> List[types.TextContent]:
    """
    Clear authentication settings from API client.

    Returns:
        List of TextContent với confirmation message
    """
    try:
        context = await get_service_context()
        
        if not context.api_client:
            return [types.TextContent(
                type="text",
                text="Error: API client not initialized. Use api_init first."
            )]

        if "Authorization" in context.api_client.session.headers:
            del context.api_client.session.headers["Authorization"]
            
        return [types.TextContent(
            type="text",
            text="Authentication settings cleared successfully"
        )]
        
    except Exception as e:
        error_msg = f"Failed to clear authentication settings: {str(e)}"
        logger.error(error_msg)
        return [types.TextContent(
            type="text",
            text=error_msg
        )]
