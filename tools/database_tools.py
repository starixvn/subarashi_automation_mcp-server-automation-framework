from mcp.server.fastmcp import FastMCP, Context
from context import ServerContext
from services import DatabaseService


def register_database_tools(app: FastMCP, server_context: ServerContext) -> None:
    @app.tool(description="Connect to a database")
    async def db_connect(connection_string: str, context: Context) -> str:
        service = DatabaseService(server_context)
        result = await service.connect(connection_string)
        return (
            "Database connected successfully"
            if result.success
            else f"Connection failed: {result.error}"
        )

    @app.tool(description="Execute a SQL query")
    async def db_query(sql: str, context: Context) -> str:
        service = DatabaseService(server_context)
        result = await service.execute_query(sql)
        if result.success:
            rows = result.data["rows"]
            if not rows:
                return "Query executed successfully - no results"
            output = f"Query Results ({len(rows)} rows):\n\n"
            for row in rows:
                output += f"{row}\n"
            return output
        else:
            return f"Query failed: {result.error}"

    @app.tool(description="Execute a SQL command")
    async def db_execute(sql: str, context: Context) -> str:
        service = DatabaseService(server_context)
        result = await service.execute_command(sql)
        if result.success:
            affected = result.data.get("affected_rows", 0)
            return f"Command executed successfully - {affected} rows affected"
        else:
            return f"Execute failed: {result.error}"

    @app.tool(description="Close the database connection")
    async def db_close(context: Context) -> str:
        service = DatabaseService(server_context)
        result = await service.close_connection()
        return (
            "Database connection closed"
            if result.success
            else f"Close failed: {result.error}"
        )
