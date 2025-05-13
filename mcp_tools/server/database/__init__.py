"""
MCP Database module for SQL Server database operations.
"""

from mcp_tools.server.database.sql_server_client import SQLServerClient
from mcp_tools.server.database.sql_server_tools import (
    db_connect,
    db_connect_with_string,
    db_query,
    db_execute,
    db_execute_many,
    db_execute_script,
    db_get_tables,
    db_get_columns,
    db_close,
)

__all__ = [
    "SQLServerClient",
    "db_connect",
    "db_connect_with_string",
    "db_query",
    "db_execute",
    "db_execute_many",
    "db_execute_script",
    "db_get_tables",
    "db_get_columns",
    "db_close",
]
