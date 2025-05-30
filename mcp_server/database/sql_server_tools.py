import logging
import json
from typing import List, Any, Optional, Union
from mcp import types
from mcp_server.core.mcp_setup import mcp, get_service_context
from mcp_server.database.sql_server_client import SQLServerClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@mcp.tool(name="db_connect", description="Connect to a SQL Server database")
async def db_connect(
    server: str,
    database: str,
    username: Optional[str] = None,
    password: Optional[str] = None,
    trusted_connection: bool = False,
) -> List[types.TextContent]:
    """
    Connect to a SQL Server database.

    Args:
        server: SQL Server name/address
        database: Database name
        username: SQL Server username (leave empty for trusted connection)
        password: SQL Server password (leave empty for trusted connection)
        trusted_connection: Use Windows authentication instead of username/password

    Returns:
        List of TextContent với connection status message
    """
    try:
        context = await get_service_context()
        
        sql_client = SQLServerClient(
            server=server,
            database=database,
            username=username,
            password=password,
            trusted_connection=trusted_connection,
        )

        if sql_client.test_connection():
            context.sql_client = sql_client
            return [types.TextContent(
                type="text",
                text=f"Successfully connected to database '{database}' on server '{server}'"
            )]
        else:
            return [types.TextContent(
                type="text",
                text=f"Failed to connect to database '{database}' on server '{server}'"
            )]
            
    except Exception as e:
        logger.error(f"Error connecting to database: {str(e)}")
        return [types.TextContent(
            type="text",
            text=f"Error connecting to database: {str(e)}"
        )]


@mcp.tool(
    name="db_connect_with_string",
    description="Connect to a SQL Server database using a connection string",
)
async def db_connect_with_string(connection_string: str) -> List[types.TextContent]:
    """
    Connect to a SQL Server database using a custom connection string.

    Args:
        connection_string: Full ODBC connection string

    Returns:
        List of TextContent với connection status message
    """
    try:
        context = await get_service_context()
        
        sql_client = SQLServerClient(
            server="placeholder",
            database="placeholder",
            connection_string=connection_string,
        )

        if sql_client.test_connection():
            context.sql_client = sql_client
            return [types.TextContent(
                type="text",
                text="Successfully connected to database using custom connection string"
            )]
        else:
            return [types.TextContent(
                type="text",
                text="Failed to connect using custom connection string"
            )]
            
    except Exception as e:
        logger.error(f"Error connecting to database: {str(e)}")
        return [types.TextContent(
            type="text",
            text=f"Error connecting to database: {str(e)}"
        )]


@mcp.tool(name="db_query", description="Execute a SELECT query and return results")
async def db_query(query: str, params: Optional[List[Any]] = None) -> List[types.TextContent]:
    """
    Execute a SELECT query on the connected database.

    Args:
        query: SQL query to execute
        params: Optional parameters for the query

    Returns:
        List of TextContent với query results as JSON
    """
    try:
        context = await get_service_context()
        
        if context.sql_client is None:
            return [types.TextContent(
                type="text",
                text="Error: Not connected to a database. Use db_connect first."
            )]

        results = context.sql_client.execute_query(query, params)
        return [types.TextContent(
            type="text",
            text=json.dumps(results, default=str, indent=2)
        )]
        
    except Exception as e:
        logger.error(f"Error executing query: {str(e)}")
        return [types.TextContent(
            type="text",
            text=f"Error executing query: {str(e)}"
        )]


@mcp.tool(
    name="db_execute",
    description="Execute a non-query SQL statement (INSERT, UPDATE, DELETE)",
)
async def db_execute(query: str, params: Optional[List[Any]] = None) -> List[types.TextContent]:
    """
    Execute a non-query SQL statement on the connected database.

    Args:
        query: SQL statement to execute
        params: Optional parameters for the statement

    Returns:
        List of TextContent với rows affected message
    """
    try:
        context = await get_service_context()
        
        if context.sql_client is None:
            return [types.TextContent(
                type="text",
                text="Error: Not connected to a database. Use db_connect first."
            )]

        affected = context.sql_client.execute_non_query(query, params)
        if affected >= 0:
            return [types.TextContent(
                type="text",
                text=f"Statement executed successfully. Rows affected: {affected}"
            )]
        else:
            return [types.TextContent(
                type="text",
                text="Error executing statement. See logs for details."
            )]
            
    except Exception as e:
        logger.error(f"Error executing statement: {str(e)}")
        return [types.TextContent(
            type="text",
            text=f"Error executing statement: {str(e)}"
        )]


@mcp.tool(
    name="db_execute_many",
    description="Execute a SQL statement with multiple parameter sets",
)
async def db_execute_many(query: str, params_list: List[List[Any]]) -> List[types.TextContent]:
    """
    Execute the same SQL statement with multiple parameter sets.

    Args:
        query: SQL statement to execute
        params_list: List of parameter sets

    Returns:
        List of TextContent với total rows affected message
    """
    try:
        context = await get_service_context()
        
        if context.sql_client is None:
            return [types.TextContent(
                type="text",
                text="Error: Not connected to a database. Use db_connect first."
            )]

        affected = context.sql_client.execute_many(query, params_list)
        if affected >= 0:
            return [types.TextContent(
                type="text",
                text=f"Batch executed successfully. Total rows affected: {affected}"
            )]
        else:
            return [types.TextContent(
                type="text",
                text="Error executing batch. See logs for details."
            )]
            
    except Exception as e:
        logger.error(f"Error executing batch: {str(e)}")
        return [types.TextContent(
            type="text",
            text=f"Error executing batch: {str(e)}"
        )]


@mcp.tool(name="db_execute_script", description="Execute a multi-statement SQL script")
async def db_execute_script(script: str) -> List[types.TextContent]:
    """
    Execute a multi-statement SQL script.

    Args:
        script: SQL script to execute

    Returns:
        List of TextContent với success or error message
    """
    try:
        context = await get_service_context()
        
        if context.sql_client is None:
            return [types.TextContent(
                type="text",
                text="Error: Not connected to a database. Use db_connect first."
            )]

        success = context.sql_client.execute_script(script)
        if success:
            return [types.TextContent(
                type="text",
                text="Script executed successfully"
            )]
        else:
            return [types.TextContent(
                type="text",
                text="Error executing script. See logs for details."
            )]
            
    except Exception as e:
        logger.error(f"Error executing script: {str(e)}")
        return [types.TextContent(
            type="text",
            text=f"Error executing script: {str(e)}"
        )]


@mcp.tool(
    name="db_get_tables", 
    description="Get a list of tables in the connected database"
)
async def db_get_tables() -> List[types.TextContent]:
    """
    Get a list of tables in the connected database.

    Returns:
        List of TextContent với table names as JSON
    """
    try:
        context = await get_service_context()
        
        if context.sql_client is None:
            return [types.TextContent(
                type="text",
                text="Error: Not connected to a database. Use db_connect first."
            )]

        tables = context.sql_client.get_tables()
        return [types.TextContent(
            type="text",
            text=json.dumps(tables, indent=2)
        )]
        
    except Exception as e:
        logger.error(f"Error getting tables: {str(e)}")
        return [types.TextContent(
            type="text",
            text=f"Error getting tables: {str(e)}"
        )]


@mcp.tool(name="db_get_columns", description="Get column information for a table")
async def db_get_columns(table_name: str) -> List[types.TextContent]:
    """
    Get column information for a table.

    Args:
        table_name: Name of the table

    Returns:
        List of TextContent với column information as JSON
    """
    try:
        context = await get_service_context()
        
        if context.sql_client is None:
            return [types.TextContent(
                type="text",
                text="Error: Not connected to a database. Use db_connect first."
            )]

        columns = context.sql_client.get_columns(table_name)
        return [types.TextContent(
            type="text",
            text=json.dumps(columns, default=str, indent=2)
        )]
        
    except Exception as e:
        logger.error(f"Error getting columns: {str(e)}")
        return [types.TextContent(
            type="text",
            text=f"Error getting columns: {str(e)}"
        )]


@mcp.tool(name="db_close", description="Close the database connection")
async def db_close() -> List[types.TextContent]:
    """
    Close the database connection.

    Returns:
        List of TextContent với confirmation message
    """
    try:
        context = await get_service_context()
        
        if context.sql_client is None:
            return [types.TextContent(
                type="text",
                text="No active database connection to close"
            )]

        context.sql_client.close()
        context.sql_client = None
        
        return [types.TextContent(
            type="text",
            text="Database connection closed successfully"
        )]
        
    except Exception as e:
        logger.error(f"Error closing connection: {str(e)}")
        return [types.TextContent(
            type="text",
            text=f"Error closing connection: {str(e)}"
        )]
