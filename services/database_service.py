from typing import Dict, Any, Optional
import aioodbc
from .base_service import BaseService, ServiceResult

_connections: Dict[str, Any] = {}


class DatabaseService(BaseService):
    def __init__(self, context):
        super().__init__(context)

    async def connect(
        self,
        host: str,
        database: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        connection_name: Optional[str] = None,
        port: Optional[int] = None,
        packet_size: Optional[int] = None,
        trust_server_certificate: Optional[bool] = None,
        integrated_security: Optional[bool] = None,
        connection_timeout: Optional[int] = None,
    ) -> ServiceResult:
        try:
            username = username or "vnTestAutomation"
            password = password or "@TestAutomation#"
            connection_name = connection_name or "default"
            port = port or 1433

            connection_string_parts = [
                "DRIVER={ODBC Driver 17 for SQL Server}",
                f"SERVER={host},{port}",
                f"DATABASE={database}",
                f"UID={username}",
                f"PWD={password}",
            ]

            if packet_size:
                connection_string_parts.append(f"PACKET SIZE={packet_size}")

            if trust_server_certificate is not None:
                trust_value = "yes" if trust_server_certificate else "no"
                connection_string_parts.append(f"TrustServerCertificate={trust_value}")

            if integrated_security is not None:
                security_value = "SSPI" if integrated_security else "false"
                connection_string_parts.append(f"Integrated Security={security_value}")

            if connection_timeout:
                connection_string_parts.append(
                    f"Connection Timeout={connection_timeout}"
                )

            connection_string = ";".join(connection_string_parts)

            connection = await aioodbc.connect(dsn=connection_string)

            _connections[connection_name] = {
                "type": "sqlserver",
                "connection": connection,
            }

            return ServiceResult(
                success=True,
                message=f"Successfully connected to SQL Server database '{database}' on {host}:{port} as connection '{connection_name}'",
                data={
                    "connection_name": connection_name,
                    "database": database,
                    "host": host,
                    "port": port,
                },
            )

        except Exception as e:
            return ServiceResult(
                success=False,
                message=f"Database connection failed: {str(e)}",
                error=str(e),
            )

    async def execute_query(
        self, sql: str, connection_name: Optional[str] = None
    ) -> ServiceResult:
        try:
            connection_name = connection_name or "default"

            if connection_name not in _connections:
                return ServiceResult(
                    success=False,
                    message=f"Connection '{connection_name}' not found. Please connect first.",
                    error="connection_not_found",
                )

            conn_info = _connections[connection_name]
            connection = conn_info["connection"]

            cursor = await connection.cursor()
            await cursor.execute(sql)

            columns = (
                [desc[0] for desc in cursor.description] if cursor.description else []
            )
            rows = await cursor.fetchall()
            await cursor.close()

            if not rows:
                return ServiceResult(
                    success=True,
                    message="Query executed successfully. No results returned.",
                    data={"columns": columns, "rows": [], "row_count": 0},
                )

            formatted_rows = []
            for row in rows:
                formatted_rows.append(dict(zip(columns, row)))

            result_text = f"Query Results ({len(rows)} rows):\n\n"
            if columns:
                result_text += " | ".join(columns) + "\n"
                result_text += "-" * (len(" | ".join(columns))) + "\n"

            for row in rows[:10]:  # Limit to first 10 rows for display
                result_text += " | ".join(str(cell) for cell in row) + "\n"

            if len(rows) > 10:
                result_text += f"... and {len(rows) - 10} more rows\n"

            return ServiceResult(
                success=True,
                message=f"Query executed successfully. {len(rows)} rows returned.",
                data={
                    "columns": columns,
                    "rows": formatted_rows,
                    "row_count": len(rows),
                    "formatted_result": result_text,
                },
            )

        except Exception as e:
            return ServiceResult(
                success=False, message=f"Query execution failed: {str(e)}", error=str(e)
            )

    async def execute_command(
        self, sql: str, connection_name: Optional[str] = None
    ) -> ServiceResult:
        try:
            connection_name = connection_name or "default"

            if connection_name not in _connections:
                return ServiceResult(
                    success=False,
                    message=f"Connection '{connection_name}' not found. Please connect first.",
                    error="connection_not_found",
                )

            conn_info = _connections[connection_name]
            connection = conn_info["connection"]

            cursor = await connection.cursor()
            await cursor.execute(sql)
            rows_affected = cursor.rowcount
            await connection.commit()
            await cursor.close()

            return ServiceResult(
                success=True,
                message=f"Statement executed successfully. Rows affected: {rows_affected}",
                data={"rows_affected": rows_affected},
            )

        except Exception as e:
            return ServiceResult(
                success=False,
                message=f"Statement execution failed: {str(e)}",
                error=str(e),
            )

    async def close_connection(
        self, connection_name: Optional[str] = None
    ) -> ServiceResult:
        try:
            connection_name = connection_name or "default"

            if connection_name not in _connections:
                return ServiceResult(
                    success=False,
                    message=f"Connection '{connection_name}' not found.",
                    error="connection_not_found",
                )

            conn_info = _connections[connection_name]
            connection = conn_info["connection"]

            await connection.close()
            del _connections[connection_name]

            return ServiceResult(
                success=True,
                message=f"Connection '{connection_name}' closed successfully.",
                data={"connection_name": connection_name},
            )

        except Exception as e:
            return ServiceResult(
                success=False,
                message=f"Failed to close connection: {str(e)}",
                error=str(e),
            )
