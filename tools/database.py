import asyncio
import json
from typing import Dict, Any, List, Optional, TYPE_CHECKING
import aioodbc

from .tool_schema import (
    define_tool_factory,
    ToolCapability,
    ToolType,
    ToolResult,
    ToolActionResult,
    Tool,
    ToolSchema,
)
from .schemas import (
    DatabaseConnectInputSchema,
    DatabaseQueryInputSchema,
    DatabaseExecuteInputSchema,
    DatabaseListTablesInputSchema,
    DatabaseDescribeTableInputSchema,
    DatabaseCloseInputSchema,
)

if TYPE_CHECKING:
    from ..context import ServerContext

_connections: Dict[str, Any] = {}


@define_tool_factory(
    capability=ToolCapability.DATABASE,
    name="db_connect",
    title="Connect to SQL Server",
    description="Connect to SQL Server database (uses default credentials if not provided)",
    input_schema=DatabaseConnectInputSchema,
    tool_type=ToolType.DESTRUCTIVE,
)
def db_connect_factory(capture_snapshot: bool) -> Tool:
    async def handle(context: "ServerContext", params: Dict[str, Any]) -> ToolResult:
        validated_params = DatabaseConnectInputSchema(**params)

        code = [
            f"// Connecting to SQL Server database",
            f"const connection = await connect('{validated_params.host}:{validated_params.port or 1433}');",
            f"// Using {'provided' if validated_params.username else 'default'} credentials",
        ]

        async def action() -> ToolActionResult:
            try:
                host = validated_params.host
                database = validated_params.database
                username = validated_params.username or "vnTestAutomation"
                password = validated_params.password or "@TestAutomation#"
                connection_name = validated_params.connection_name or "default"
                port = validated_params.port or 1433

                connection_string_parts = [
                    "DRIVER={ODBC Driver 17 for SQL Server}",
                    f"SERVER={host},{port}",
                    f"DATABASE={database}",
                    f"UID={username}",
                    f"PWD={password}"
                ]
                
                if validated_params.packet_size:
                    connection_string_parts.append(f"PACKET SIZE={validated_params.packet_size}")
                
                if validated_params.trust_server_certificate is not None:
                    trust_value = "yes" if validated_params.trust_server_certificate else "no"
                    connection_string_parts.append(f"TrustServerCertificate={trust_value}")
                
                if validated_params.integrated_security is not None:
                    security_value = "SSPI" if validated_params.integrated_security else "false"
                    connection_string_parts.append(f"Integrated Security={security_value}")
                
                if validated_params.connection_timeout:
                    connection_string_parts.append(f"Connection Timeout={validated_params.connection_timeout}")

                connection_string = ";".join(connection_string_parts)

                connection = await aioodbc.connect(dsn=connection_string)

                _connections[connection_name] = {
                    "type": "sqlserver",
                    "connection": connection,
                }

                return ToolActionResult(
                    content=[
                        {
                            "type": "text",
                            "text": f"Successfully connected to SQL Server database '{database}' on {host}:{port} as connection '{connection_name}'",
                        }
                    ]
                )

            except Exception as e:
                return ToolActionResult(
                    content=[
                        {
                            "type": "text",
                            "text": f"Database connection failed: {str(e)}",
                        }
                    ]
                )

        return ToolResult(
            code=code,
            action=action,
            capture_snapshot=False,
            wait_for_network=False,
        )

    schema = ToolSchema(
        name="db_connect",
        title="Connect to SQL Server",
        description="Connect to SQL Server database (uses default credentials if not provided)",
        input_schema=DatabaseConnectInputSchema,
        tool_type=ToolType.DESTRUCTIVE,
    )

    return Tool(
        capability=ToolCapability.DATABASE,
        schema=schema,
        handle=handle,
        browser_independent=True,
    )


@define_tool_factory(
    capability=ToolCapability.DATABASE,
    name="db_query",
    title="Execute Query",
    description="Execute SELECT query and return results",
    input_schema=DatabaseQueryInputSchema,
    tool_type=ToolType.READ_ONLY,
)
def db_query_factory(capture_snapshot: bool) -> Tool:
    async def handle(context: "ServerContext", params: Dict[str, Any]) -> ToolResult:
        validated_params = DatabaseQueryInputSchema(**params)

        code = [
            f"// Executing database query",
            f"const result = await connection.query(`{validated_params.query}`);",
        ]

        async def action() -> ToolActionResult:
            try:
                connection_name = validated_params.connection_name or "default"
                query = validated_params.query
                query_params = validated_params.params or []

                if connection_name not in _connections:
                    return ToolActionResult(
                        content=[
                            {
                                "type": "text",
                                "text": f"Connection '{connection_name}' not found. Please connect first.",
                            }
                        ],
                        
                    )

                conn_info = _connections[connection_name]
                connection = conn_info["connection"]

                async with connection.cursor() as cursor:
                    if query_params:
                        await cursor.execute(query, query_params)
                    else:
                        await cursor.execute(query)

                    rows = await cursor.fetchall()
                    columns = (
                        [desc[0] for desc in cursor.description]
                        if cursor.description
                        else []
                    )
                    data = [list(row) for row in rows] if rows else []

                result_text = (
                    f"Query executed successfully. {len(data)} rows returned.\n\n"
                )

                if columns and data:
                    result_text += "Columns: " + ", ".join(columns) + "\n\n"
                    result_text += "Results:\n"
                    for i, row in enumerate(data[:100]):
                        result_text += f"Row {i + 1}: {dict(zip(columns, row))}\n"

                    if len(data) > 100:
                        result_text += f"\n... and {len(data) - 100} more rows"

                return ToolActionResult(content=[{"type": "text", "text": result_text}])

            except Exception as e:
                return ToolActionResult(
                    content=[
                        {"type": "text", "text": f"Query execution failed: {str(e)}"}
                    ],
                    
                )

        return ToolResult(
            code=code,
            action=action,
            capture_snapshot=False,
            wait_for_network=False,
        )

    schema = ToolSchema(
        name="db_query",
        title="Execute Query",
        description="Execute SELECT query and return results",
        input_schema=DatabaseQueryInputSchema,
        tool_type=ToolType.READ_ONLY,
    )

    return Tool(
        capability=ToolCapability.DATABASE,
        schema=schema,
        handle=handle,
        browser_independent=True,
    )


@define_tool_factory(
    capability=ToolCapability.DATABASE,
    name="db_execute",
    title="Execute Statement",
    description="Execute INSERT, UPDATE, DELETE statements",
    input_schema=DatabaseExecuteInputSchema,
    tool_type=ToolType.DESTRUCTIVE,
)
def db_execute_factory(capture_snapshot: bool) -> Tool:
    async def handle(context: "ServerContext", params: Dict[str, Any]) -> ToolResult:
        validated_params = DatabaseExecuteInputSchema(**params)

        code = [
            f"// Executing database statement",
            f"const result = await connection.execute(`{validated_params.query}`);",
        ]

        async def action() -> ToolActionResult:
            try:
                connection_name = validated_params.connection_name or "default"
                statement = validated_params.query
                statement_params = validated_params.params or []

                if connection_name not in _connections:
                    return ToolActionResult(
                        content=[
                            {
                                "type": "text",
                                "text": f"Connection '{connection_name}' not found. Please connect first.",
                            }
                        ],
                        
                    )

                conn_info = _connections[connection_name]
                connection = conn_info["connection"]

                async with connection.cursor() as cursor:
                    if statement_params:
                        await cursor.execute(statement, statement_params)
                    else:
                        await cursor.execute(statement)

                    rows_affected = cursor.rowcount
                    await connection.commit()

                    return ToolActionResult(
                        content=[
                            {
                                "type": "text",
                                "text": f"Statement executed successfully. Rows affected: {rows_affected}",
                            }
                        ]
                    )

            except Exception as e:
                return ToolActionResult(
                    content=[
                        {
                            "type": "text",
                            "text": f"Statement execution failed: {str(e)}",
                        }
                    ],
                    
                )

        return ToolResult(
            code=code,
            action=action,
            capture_snapshot=False,
            wait_for_network=False,
        )

    schema = ToolSchema(
        name="db_execute",
        title="Execute Statement",
        description="Execute INSERT, UPDATE, DELETE statements",
        input_schema=DatabaseExecuteInputSchema,
        tool_type=ToolType.DESTRUCTIVE,
    )

    return Tool(
        capability=ToolCapability.DATABASE,
        schema=schema,
        handle=handle,
        browser_independent=True,
    )


@define_tool_factory(
    capability=ToolCapability.DATABASE,
    name="db_list_tables",
    title="List Tables",
    description="List all tables in the database",
    input_schema=DatabaseListTablesInputSchema,
    tool_type=ToolType.READ_ONLY,
)
def db_list_tables_factory(capture_snapshot: bool) -> Tool:
    async def handle(context: "ServerContext", params: Dict[str, Any]) -> ToolResult:
        validated_params = DatabaseListTablesInputSchema(**params)

        code = [
            f"// Listing database tables",
            f"const tables = await connection.query('SELECT table_name FROM information_schema.tables');",
        ]

        async def action() -> ToolActionResult:
            try:
                connection_name = validated_params.connection_name or "default"
                schema_name = validated_params.schema_name

                if connection_name not in _connections:
                    return ToolActionResult(
                        content=[
                            {
                                "type": "text",
                                "text": f"Connection '{connection_name}' not found. Please connect first.",
                            }
                        ],
                        
                    )

                conn_info = _connections[connection_name]
                connection = conn_info["connection"]
                async with connection.cursor() as cursor:
                    if schema_name:
                        query = """
                            SELECT TABLE_SCHEMA, TABLE_NAME, TABLE_TYPE
                            FROM INFORMATION_SCHEMA.TABLES
                            WHERE TABLE_SCHEMA = ?
                            ORDER BY TABLE_NAME
                        """
                        await cursor.execute(query, (schema_name,))
                    else:
                        query = """
                            SELECT TABLE_SCHEMA, TABLE_NAME, TABLE_TYPE
                            FROM INFORMATION_SCHEMA.TABLES
                            ORDER BY TABLE_SCHEMA, TABLE_NAME
                        """
                        await cursor.execute(query)

                    rows = await cursor.fetchall()
                    columns = [desc[0] for desc in cursor.description]
                    rows = [dict(zip(columns, row)) for row in rows]

                if not rows:
                    return ToolActionResult(
                        content=[
                            {
                                "type": "text",
                                "text": "No tables found in the database.",
                            }
                        ]
                    )

                result_text = f"Found {len(rows)} tables:\n\n"

                for row in rows:
                    if schema_name:
                        result_text += (
                            f"- {row.get('table_name')} ({row.get('table_type')})\n"
                        )
                    else:
                        result_text += f"- {row.get('table_schema')}.{row.get('table_name')} ({row.get('table_type')})\n"

                return ToolActionResult(content=[{"type": "text", "text": result_text}])

            except Exception as e:
                return ToolActionResult(
                    content=[
                        {"type": "text", "text": f"Failed to list tables: {str(e)}"}
                    ],
                    
                )

        return ToolResult(
            code=code,
            action=action,
            capture_snapshot=False,
            wait_for_network=False,
        )

    schema = ToolSchema(
        name="db_list_tables",
        title="List Tables",
        description="List all tables in the database",
        input_schema=DatabaseListTablesInputSchema,
        tool_type=ToolType.READ_ONLY,
    )

    return Tool(
        capability=ToolCapability.DATABASE,
        schema=schema,
        handle=handle,
        browser_independent=True,
    )


@define_tool_factory(
    capability=ToolCapability.DATABASE,
    name="db_describe_table",
    title="Describe Table",
    description="Get table structure and column information",
    input_schema=DatabaseDescribeTableInputSchema,
    tool_type=ToolType.READ_ONLY,
)
def db_describe_table_factory(capture_snapshot: bool) -> Tool:
    async def handle(context: "ServerContext", params: Dict[str, Any]) -> ToolResult:
        validated_params = DatabaseDescribeTableInputSchema(**params)

        code = [
            f"// Describing table structure",
            f"const columns = await connection.query('DESCRIBE {validated_params.table_name}');",
        ]

        async def action() -> ToolActionResult:
            try:
                connection_name = validated_params.connection_name or "default"
                table_name = validated_params.table_name
                schema_name = validated_params.schema_name

                if connection_name not in _connections:
                    return ToolActionResult(
                        content=[
                            {
                                "type": "text",
                                "text": f"Connection '{connection_name}' not found. Please connect first.",
                            }
                        ],
                        
                    )

                conn_info = _connections[connection_name]
                connection = conn_info["connection"]

                async with connection.cursor() as cursor:
                    if schema_name:
                        query = """
                            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT, CHARACTER_MAXIMUM_LENGTH
                            FROM INFORMATION_SCHEMA.COLUMNS
                            WHERE TABLE_NAME = ? AND TABLE_SCHEMA = ?
                            ORDER BY ORDINAL_POSITION
                        """
                        await cursor.execute(query, (table_name, schema_name))
                    else:
                        query = """
                            SELECT COLUMN_NAME, DATA_TYPE, IS_NULLABLE, COLUMN_DEFAULT, CHARACTER_MAXIMUM_LENGTH
                            FROM INFORMATION_SCHEMA.COLUMNS
                            WHERE TABLE_NAME = ?
                            ORDER BY ORDINAL_POSITION
                        """
                        await cursor.execute(query, (table_name,))

                    rows = await cursor.fetchall()
                    columns = [desc[0] for desc in cursor.description]
                    rows = [dict(zip(columns, row)) for row in rows]

                if not rows:
                    return ToolActionResult(
                        content=[
                            {
                                "type": "text",
                                "text": f"Table '{table_name}' not found or no columns.",
                            }
                        ],
                        
                    )

                full_table_name = (
                    f"{schema_name}.{table_name}" if schema_name else table_name
                )
                result_text = f"Table: {full_table_name}\n\n"
                result_text += "Columns:\n"

                for row in rows:
                    column_name = row.get("column_name")
                    data_type = row.get("data_type")
                    is_nullable = row.get("is_nullable")
                    column_default = row.get("column_default")
                    max_length = row.get("character_maximum_length")

                    type_info = data_type
                    if max_length:
                        type_info += f"({max_length})"

                    nullable = "NULL" if is_nullable == "YES" else "NOT NULL"
                    default = f"DEFAULT {column_default}" if column_default else ""

                    result_text += (
                        f"  - {column_name}: {type_info} {nullable} {default}\n"
                    )

                return ToolActionResult(content=[{"type": "text", "text": result_text}])

            except Exception as e:
                return ToolActionResult(
                    content=[
                        {"type": "text", "text": f"Failed to describe table: {str(e)}"}
                    ],
                    
                )

        return ToolResult(
            code=code,
            action=action,
            capture_snapshot=False,
            wait_for_network=False,
        )

    schema = ToolSchema(
        name="db_describe_table",
        title="Describe Table",
        description="Get table structure and column information",
        input_schema=DatabaseDescribeTableInputSchema,
        tool_type=ToolType.READ_ONLY,
    )

    return Tool(
        capability=ToolCapability.DATABASE,
        schema=schema,
        handle=handle,
        browser_independent=True,
    )


@define_tool_factory(
    capability=ToolCapability.DATABASE,
    name="db_close",
    title="Close Connection",
    description="Close database connection",
    input_schema=DatabaseCloseInputSchema,
    tool_type=ToolType.DESTRUCTIVE,
)
def db_close_factory(capture_snapshot: bool) -> Tool:
    async def handle(context: "ServerContext", params: Dict[str, Any]) -> ToolResult:
        validated_params = DatabaseCloseInputSchema(**params)

        code = [
            f"// Closing database connection",
            f"await connection.close();",
        ]

        async def action() -> ToolActionResult:
            try:
                connection_name = validated_params.connection_name or "default"

                if connection_name not in _connections:
                    return ToolActionResult(
                        content=[
                            {
                                "type": "text",
                                "text": f"Connection '{connection_name}' not found.",
                            }
                        ],
                        
                    )

                conn_info = _connections[connection_name]
                connection = conn_info["connection"]

                await connection.close()

                del _connections[connection_name]

                return ToolActionResult(
                    content=[
                        {
                            "type": "text",
                            "text": f"Connection '{connection_name}' closed successfully.",
                        }
                    ]
                )

            except Exception as e:
                return ToolActionResult(
                    content=[
                        {
                            "type": "text",
                            "text": f"Failed to close connection: {str(e)}",
                        }
                    ],
                    
                )

        return ToolResult(
            code=code,
            action=action,
            capture_snapshot=False,
            wait_for_network=False,
        )

    schema = ToolSchema(
        name="db_close",
        title="Close Connection",
        description="Close database connection",
        input_schema=DatabaseCloseInputSchema,
        tool_type=ToolType.DESTRUCTIVE,
    )

    return Tool(
        capability=ToolCapability.DATABASE,
        schema=schema,
        handle=handle,
        browser_independent=True,
    )


def get_database_tools(capture_snapshot: bool = True) -> list[Tool]:
    return [
        db_connect_factory(capture_snapshot),
        db_query_factory(capture_snapshot),
        db_execute_factory(capture_snapshot),
        db_list_tables_factory(capture_snapshot),
        db_describe_table_factory(capture_snapshot),
        db_close_factory(capture_snapshot),
    ]


DATABASE_TOOLS = get_database_tools()
