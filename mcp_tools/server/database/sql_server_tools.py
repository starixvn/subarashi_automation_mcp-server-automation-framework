"""
MCP tools for SQL Server database operations.
"""

import logging
import json
from typing import Dict, Any, Optional, List, Union
from mcp_tools.server.core.mcp_setup import mcp
from mcp_tools.server.database.sql_server_client import SQLServerClient

# Global instance of SQL Server client
sql_client = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@mcp.tool(name="DB-Connect", description="Connect to a SQL Server database")
def db_connect(
    server: str,
    database: str,
    username: Optional[str] = None,
    password: Optional[str] = None,
    trusted_connection: bool = False,
) -> str:
    """
    Connect to a SQL Server database.

    Args:
        server: SQL Server name/address
        database: Database name
        username: SQL Server username (leave empty for trusted connection)
        password: SQL Server password (leave empty for trusted connection)
        trusted_connection: Use Windows authentication instead of username/password

    Returns:
        Connection status message
    """
    global sql_client

    try:
        sql_client = SQLServerClient(
            server=server,
            database=database,
            username=username,
            password=password,
            trusted_connection=trusted_connection,
        )

        if sql_client.test_connection():
            return f"Connected to database '{database}' on server '{server}'"
        else:
            return f"Failed to connect to database '{database}' on server '{server}'"
    except Exception as e:
        logger.error(f"Error connecting to database: {str(e)}")
        return f"Error connecting to database: {str(e)}"


@mcp.tool(
    name="DB-Connect-With-String",
    description="Connect to a SQL Server database using a connection string",
)
def db_connect_with_string(connection_string: str) -> str:
    """
    Connect to a SQL Server database using a custom connection string.

    Args:
        connection_string: Full ODBC connection string

    Returns:
        Connection status message
    """
    global sql_client

    try:
        # Server and database are required but will be overridden by the connection string
        sql_client = SQLServerClient(
            server="placeholder",
            database="placeholder",
            connection_string=connection_string,
        )

        if sql_client.test_connection():
            return "Connected to database using custom connection string"
        else:
            return "Failed to connect using custom connection string"
    except Exception as e:
        logger.error(f"Error connecting to database: {str(e)}")
        return f"Error connecting to database: {str(e)}"


@mcp.tool(name="DB-Query", description="Execute a SELECT query and return results")
def db_query(query: str, params: Optional[List[Any]] = None) -> str:
    """
    Execute a SELECT query on the connected database.

    Args:
        query: SQL query to execute
        params: Optional parameters for the query

    Returns:
        JSON string with query results
    """
    global sql_client

    if sql_client is None:
        return "Error: Not connected to a database. Use db_connect first."

    try:
        results = sql_client.execute_query(query, params)
        return json.dumps(results, default=str)
    except Exception as e:
        logger.error(f"Error executing query: {str(e)}")
        return f"Error executing query: {str(e)}"


@mcp.tool(
    name="DB-Execute",
    description="Execute a non-query SQL statement (INSERT, UPDATE, DELETE)",
)
def db_execute(query: str, params: Optional[List[Any]] = None) -> str:
    """
    Execute a non-query SQL statement on the connected database.

    Args:
        query: SQL statement to execute
        params: Optional parameters for the statement

    Returns:
        Message with rows affected
    """
    global sql_client

    if sql_client is None:
        return "Error: Not connected to a database. Use db_connect first."

    try:
        affected = sql_client.execute_non_query(query, params)
        if affected >= 0:
            return f"Statement executed successfully. Rows affected: {affected}"
        else:
            return "Error executing statement. See logs for details."
    except Exception as e:
        logger.error(f"Error executing statement: {str(e)}")
        return f"Error executing statement: {str(e)}"


@mcp.tool(
    name="DB-Execute-Many",
    description="Execute a SQL statement with multiple parameter sets",
)
def db_execute_many(query: str, params_list: List[List[Any]]) -> str:
    """
    Execute the same SQL statement with multiple parameter sets.

    Args:
        query: SQL statement to execute
        params_list: List of parameter sets

    Returns:
        Message with total rows affected
    """
    global sql_client

    if sql_client is None:
        return "Error: Not connected to a database. Use db_connect first."

    try:
        affected = sql_client.execute_many(query, params_list)
        if affected >= 0:
            return f"Batch executed successfully. Total rows affected: {affected}"
        else:
            return "Error executing batch. See logs for details."
    except Exception as e:
        logger.error(f"Error executing batch: {str(e)}")
        return f"Error executing batch: {str(e)}"


@mcp.tool(name="DB-Execute-Script", description="Execute a multi-statement SQL script")
def db_execute_script(script: str) -> str:
    """
    Execute a multi-statement SQL script.

    Args:
        script: SQL script to execute

    Returns:
        Success or error message
    """
    global sql_client

    if sql_client is None:
        return "Error: Not connected to a database. Use db_connect first."

    try:
        success = sql_client.execute_script(script)
        if success:
            return "Script executed successfully"
        else:
            return "Error executing script. See logs for details."
    except Exception as e:
        logger.error(f"Error executing script: {str(e)}")
        return f"Error executing script: {str(e)}"


@mcp.tool(
    name="DB-Get-Tables", description="Get a list of tables in the connected database"
)
def db_get_tables() -> str:
    """
    Get a list of tables in the connected database.

    Returns:
        JSON string with table names
    """
    global sql_client

    if sql_client is None:
        return "Error: Not connected to a database. Use db_connect first."

    try:
        tables = sql_client.get_tables()
        return json.dumps(tables)
    except Exception as e:
        logger.error(f"Error getting tables: {str(e)}")
        return f"Error getting tables: {str(e)}"


@mcp.tool(name="DB-Get-Columns", description="Get column information for a table")
def db_get_columns(table_name: str) -> str:
    """
    Get column information for a table.

    Args:
        table_name: Name of the table

    Returns:
        JSON string with column information
    """
    global sql_client

    if sql_client is None:
        return "Error: Not connected to a database. Use db_connect first."

    try:
        columns = sql_client.get_columns(table_name)
        return json.dumps(columns, default=str)
    except Exception as e:
        logger.error(f"Error getting columns: {str(e)}")
        return f"Error getting columns: {str(e)}"


@mcp.tool(name="DB-Close", description="Close the database connection")
def db_close() -> str:
    """
    Close the database connection.

    Returns:
        Confirmation message
    """
    global sql_client

    if sql_client is None:
        return "No active database connection to close"

    try:
        sql_client.close()
        sql_client = None
        return "Database connection closed"
    except Exception as e:
        logger.error(f"Error closing connection: {str(e)}")
        return f"Error closing connection: {str(e)}"
