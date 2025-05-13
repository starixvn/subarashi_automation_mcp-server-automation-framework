"""
API authentication functionality for MCP Tools.
"""

import logging
import json
import base64
import time
from typing import Dict, Any, Optional, Union, List

from mcp_tools.server.core.mcp_setup import mcp
from mcp_tools.server.api.rest_client import api_client, RestApiClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Store for authentication tokens
tokens = {}


@mcp.tool(
    name="API-BasicAuth", description="Set up Basic Authentication for API requests."
)
async def api_basic_auth(username: str, password: str) -> str:
    """
    Set up Basic Authentication for API requests.

    Args:
        username: Username for Basic Authentication
        password: Password for Basic Authentication

    Returns:
        Confirmation message
    """
    global api_client
    if not api_client:
        return "Error: API client not initialized. Use API-Init first."

    try:
        auth_string = f"{username}:{password}"
        encoded_auth = base64.b64encode(auth_string.encode()).decode()
        api_client.session.headers.update({"Authorization": f"Basic {encoded_auth}"})
        return "Basic Authentication set up successfully"
    except Exception as e:
        error_msg = f"Failed to set up Basic Authentication: {str(e)}"
        logger.error(error_msg)
        return error_msg


@mcp.tool(
    name="API-BearerToken",
    description="Set up Bearer Token Authentication for API requests.",
)
async def api_bearer_token(token: str) -> str:
    """
    Set up Bearer Token Authentication for API requests.

    Args:
        token: Bearer token for Authentication

    Returns:
        Confirmation message
    """
    global api_client
    if not api_client:
        return "Error: API client not initialized. Use API-Init first."

    try:
        api_client.session.headers.update({"Authorization": f"Bearer {token}"})
        return "Bearer Token Authentication set up successfully"
    except Exception as e:
        error_msg = f"Failed to set up Bearer Token Authentication: {str(e)}"
        logger.error(error_msg)
        return error_msg


@mcp.tool(
    name="API-OAuth2",
    description="Get OAuth2 token using client credentials flow and set it for API requests.",
)
async def api_oauth2_client_credentials(
    token_url: str, client_id: str, client_secret: str, scope: Optional[str] = None
) -> str:
    """
    Get OAuth2 token using client credentials flow and set it for API requests.

    Args:
        token_url: OAuth2 token endpoint URL
        client_id: OAuth2 client ID
        client_secret: OAuth2 client secret
        scope: Optional OAuth2 scope

    Returns:
        Confirmation message with token details
    """
    global api_client, tokens
    if not api_client:
        return "Error: API client not initialized. Use API-Init first."

    try:
        # Create data for token request
        data = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
        }

        if scope:
            data["scope"] = scope

        # Make request to token endpoint
        temp_client = RestApiClient("")
        response = temp_client.post(token_url, data=data)

        if response.status_code != 200:
            return f"Failed to get OAuth2 token: {response.text}"

        token_data = response.json()

        # Store token with expiration time
        if "expires_in" in token_data:
            token_data["expires_at"] = time.time() + token_data["expires_in"]

        token_id = f"oauth2_{client_id}"
        tokens[token_id] = token_data

        # Set token in API client
        token = token_data.get("access_token")
        api_client.session.headers.update({"Authorization": f"Bearer {token}"})

        # Return token details
        return f"OAuth2 token acquired successfully. Expires in {token_data.get('expires_in', 'unknown')} seconds."
    except Exception as e:
        error_msg = f"Failed to get OAuth2 token: {str(e)}"
        logger.error(error_msg)
        return error_msg


@mcp.tool(
    name="API-ClearAuth", description="Clear authentication settings from API client."
)
async def api_clear_auth() -> str:
    """
    Clear authentication settings from API client.

    Returns:
        Confirmation message
    """
    global api_client
    if not api_client:
        return "Error: API client not initialized. Use API-Init first."

    try:
        if "Authorization" in api_client.session.headers:
            del api_client.session.headers["Authorization"]
        return "Authentication settings cleared successfully"
    except Exception as e:
        error_msg = f"Failed to clear authentication settings: {str(e)}"
        logger.error(error_msg)
        return error_msg
