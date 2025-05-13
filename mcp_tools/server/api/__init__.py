"""
API integration functionality for MCP Tools.
Includes tools for making API requests to various services.
"""

# Import all API functions
from mcp_tools.server.api.rest_client import (
    api_init,
    api_get,
    api_post,
    api_put,
    api_delete,
)
from mcp_tools.server.api.auth import (
    api_basic_auth,
    api_bearer_token,
    api_oauth2_client_credentials,
    api_clear_auth,
)

# Export all functions for easy importing
__all__ = [
    # REST client
    "api_init",
    "api_get",
    "api_post",
    "api_put",
    "api_delete",
    # Authentication
    "api_basic_auth",
    "api_bearer_token",
    "api_oauth2_client_credentials",
    "api_clear_auth",
]
