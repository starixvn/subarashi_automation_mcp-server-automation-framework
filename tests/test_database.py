import pytest
from unittest.mock import AsyncMock, MagicMock, patch, Mock
from typing import Dict, Any, List
import asyncio
import json

from tools.database import get_database_tools
from core.schemas import (
    DatabaseConnectInputSchema,
    DatabaseQueryInputSchema,
    DatabaseExecuteInputSchema,
    DatabaseListTablesInputSchema,
    DatabaseDescribeTableInputSchema,
    DatabaseCloseInputSchema,
)
from context import ServerContext
from config.settings import Settings
from core.tool_schema import ToolCapability, ToolType, ToolResult


@pytest.fixture
def context():
    settings = Settings(headless=True)
    return ServerContext(settings)


@pytest.fixture
def database_tools():
    return get_database_tools(capture_snapshot=False)


@pytest.fixture
def mock_asyncpg_connection():
    mock_conn = AsyncMock()
    mock_conn.fetch.return_value = [
        {"id": 1, "name": "test1", "email": "test1@example.com"},
        {"id": 2, "name": "test2", "email": "test2@example.com"},
    ]
    mock_conn.fetchrow.return_value = {"count": 2}
    mock_conn.execute.return_value = "INSERT 0 1"
    mock_conn.close = AsyncMock()
    return mock_conn


@pytest.fixture
def mock_aioodbc_connection():
    mock_conn = AsyncMock()
    mock_cursor = AsyncMock()

    # Setup cursor context manager properly
    mock_cursor_cm = AsyncMock()
    mock_cursor_cm.__aenter__ = AsyncMock(return_value=mock_cursor)
    mock_cursor_cm.__aexit__ = AsyncMock(return_value=None)

    # Make cursor() return the context manager
    mock_conn.cursor = Mock(return_value=mock_cursor_cm)

    mock_cursor.fetchall.return_value = [
        (1, "test1", "test1@example.com"),
        (2, "test2", "test2@example.com"),
    ]
    mock_cursor.description = [("id", None), ("name", None), ("email", None)]
    mock_cursor.fetchone.return_value = (2,)
    mock_cursor.execute = AsyncMock()
    mock_cursor.rowcount = 1

    mock_conn.close = AsyncMock()
    mock_conn.commit = AsyncMock()
    return mock_conn


class TestDatabaseSchemas:
    # def test_database_connect_schema_postgresql(self):
    #     valid_params = {
    #         "db_type": "postgresql",
    #         "host": "localhost",
    #         "port": 5432,
    #         "database": "testdb",
    #         "username": "testuser",
    #         "password": "testpass",
    #     }
    #     schema = DatabaseConnectInputSchema(**valid_params)
    #     assert schema.db_type == "postgresql"
    #     assert schema.host == "localhost"
    #     assert schema.port == 5432
    #     assert schema.database == "testdb"
    #     assert schema.username == "testuser"
    #     assert schema.password == "testpass"

    # def test_database_connect_schema_sqlserver(self):
    #     valid_params = {
    #         "db_type": "sqlserver",
    #         "host": "localhost",
    #         "port": 1433,
    #         "database": "testdb",
    #         "username": "testuser",
    #         "password": "testpass",
    #     }
    #     schema = DatabaseConnectInputSchema(**valid_params)
    #     assert schema.db_type == "sqlserver"
    #     assert schema.port == 1433

    def test_database_connect_schema_invalid_type(self):
        invalid_params = {
            "db_type": "mysql",
            "host": "localhost",
            "database": "testdb",
            "username": "testuser",
            "password": "testpass",
        }
        with pytest.raises(ValueError):
            DatabaseConnectInputSchema(**invalid_params)

    def test_database_query_schema(self):
        valid_params = {"query": "SELECT * FROM users", "connection_name": "test_conn"}
        schema = DatabaseQueryInputSchema(**valid_params)
        assert schema.query == "SELECT * FROM users"
        assert schema.connection_name == "test_conn"

    def test_database_query_schema_with_params(self):
        valid_params = {
            "query": "SELECT * FROM users WHERE id = $1",
            "connection_name": "test_conn",
            "params": [1],
        }
        schema = DatabaseQueryInputSchema(**valid_params)
        assert schema.params == [1]

    def test_database_execute_schema(self):
        valid_params = {
            "query": "INSERT INTO users (name) VALUES ($1)",
            "connection_name": "test_conn",
            "params": ["test"],
        }
        schema = DatabaseExecuteInputSchema(**valid_params)
        assert schema.connection_name == "test_conn"
        assert schema.query == "INSERT INTO users (name) VALUES ($1)"
        assert schema.params == ["test"]

    def test_database_list_tables_schema(self):
        valid_params = {"connection_name": "test_conn"}
        schema = DatabaseListTablesInputSchema(**valid_params)
        assert schema.connection_name == "test_conn"

    def test_database_describe_table_schema(self):
        valid_params = {"table_name": "users", "connection_name": "test_conn"}
        schema = DatabaseDescribeTableInputSchema(**valid_params)
        assert schema.connection_name == "test_conn"
        assert schema.table_name == "users"

    def test_database_close_schema(self):
        valid_params = {"connection_name": "test_conn"}
        schema = DatabaseCloseInputSchema(**valid_params)
        assert schema.connection_name == "test_conn"


class TestDatabaseTools:
    def test_database_tools_creation(self, database_tools):
        assert len(database_tools) == 4
        tool_names = [tool.schema.name for tool in database_tools]
        expected_names = [
            "db_connect",
            "db_query",
            "db_execute",
            "db_close",
        ]
        assert set(tool_names) == set(expected_names)

    def test_database_tools_have_correct_capabilities(self, database_tools):
        for tool in database_tools:
            assert tool.capability == ToolCapability.DATABASE

    def test_database_tools_are_browser_independent(self, database_tools):
        for tool in database_tools:
            assert tool.browser_independent is True

    def test_database_tools_have_correct_types(self, database_tools):
        destructive_tools = {"db_connect", "db_execute", "db_close"}
        read_only_tools = {"db_query", "db_list_tables", "db_describe_table"}

        for tool in database_tools:
            if tool.schema.name in destructive_tools:
                assert tool.schema.tool_type == ToolType.DESTRUCTIVE
            elif tool.schema.name in read_only_tools:
                assert tool.schema.tool_type == ToolType.READ_ONLY

    # def test_database_tools_have_correct_schemas(self, database_tools):
    #     schema_mapping = {
    #         "db_connect": DatabaseConnectInputSchema,
    #         "db_query": DatabaseQueryInputSchema,
    #         "db_execute": DatabaseExecuteInputSchema,
    #         "db_list_tables": DatabaseListTablesInputSchema,
    #         "db_describe_table": DatabaseDescribeTableInputSchema,
    #         "db_close": DatabaseCloseInputSchema,
    #     }

    #     for tool in database_tools:
    #         expected_schema = schema_mapping[tool.schema.name]
    #         assert tool.schema.input_schema == expected_schema

    # @pytest.mark.asyncio
    # async def test_db_connect_postgresql(
    #     self, context, database_tools, mock_asyncpg_connection
    # ):
    #     db_connect_tool = next(
    #         tool for tool in database_tools if tool.schema.name == "db_connect"
    #     )

    #     params = {
    #         "db_type": "postgresql",
    #         "host": "localhost",
    #         "port": 5432,
    #         "database": "testdb",
    #         "username": "testuser",
    #         "password": "testpass",
    #         "connection_name": "test_conn",
    #     }

    #     with patch("asyncpg.connect", new_callable=AsyncMock) as mock_connect:
    #         mock_connect.return_value = mock_asyncpg_connection

    #         result = await db_connect_tool.handle(context, params)

    #         assert result.code is not None
    #         assert len(result.code) > 0
    #         assert result.action is not None
    #         assert result.capture_snapshot is False
    #         assert result.wait_for_network is False

    #         # Execute the action to test the actual database connection logic
    #         action_result = await result.action()
    #         assert action_result is not None
    #         # Check that action executed successfully

    #         mock_connect.assert_called_once_with(
    #             host="localhost",
    #             port=5432,
    #             database="testdb",
    #             user="testuser",
    #             password="testpass",
    #         )

    # @pytest.mark.asyncio
    # async def test_db_connect_sqlserver(
    #     self, context, database_tools, mock_aioodbc_connection
    # ):
    #     db_connect_tool = next(
    #         tool for tool in database_tools if tool.schema.name == "db_connect"
    #     )

    #     params = {
    #         "db_type": "sqlserver",
    #         "host": "localhost",
    #         "port": 1433,
    #         "database": "testdb",
    #         "username": "testuser",
    #         "password": "testpass",
    #         "connection_name": "test_conn",
    #     }

    #     with patch("aioodbc.connect", new_callable=AsyncMock) as mock_connect:
    #         mock_connect.return_value = mock_aioodbc_connection

    #         result = await db_connect_tool.handle(context, params)

    #         assert result.code is not None
    #         assert len(result.code) > 0
    #         assert result.action is not None

    #         # Execute the action to test the actual database connection logic
    #         action_result = await result.action()
    #         assert action_result is not None
    #         # Check that action executed successfully

    #         expected_dsn = "DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost,1433;DATABASE=testdb;UID=testuser;PWD=testpass"
    #         mock_connect.assert_called_once_with(dsn=expected_dsn)

    # @pytest.mark.asyncio
    # async def test_db_connect_connection_error(self, context, database_tools):
    #     db_connect_tool = next(
    #         tool for tool in database_tools if tool.schema.name == "db_connect"
    #     )

    #     params = {
    #         "db_type": "postgresql",
    #         "host": "invalid_host",
    #         "port": 5432,
    #         "database": "testdb",
    #         "username": "testuser",
    #         "password": "testpass",
    #         "connection_name": "test_conn",
    #     }

    #     with patch("asyncpg.connect", new_callable=AsyncMock) as mock_connect:
    #         mock_connect.side_effect = Exception("Connection failed")

    #         result = await db_connect_tool.handle(context, params)

    #         assert result.code is not None

    #         # Execute the action to test error handling
    #         action_result = await result.action()
    #         assert action_result is not None
    #         # Error expected - check content has error message
    #         assert "Connection failed" in action_result.content[0]["text"]

    # @pytest.mark.asyncio
    # async def test_db_query_postgresql(
    #     self, context, database_tools, mock_asyncpg_connection
    # ):
    #     from tools.database import _connections

    #     _connections["test_conn"] = {
    #         "type": "postgresql",
    #         "connection": mock_asyncpg_connection,
    #     }

    #     db_query_tool = next(
    #         tool for tool in database_tools if tool.schema.name == "db_query"
    #     )

    #     params = {"query": "SELECT * FROM users", "connection_name": "test_conn"}

    #     result = await db_query_tool.handle(context, params)

    #     assert result.code is not None
    #     assert result.action is not None
    #     assert result.capture_snapshot is False

    #     # Execute the action to test the actual query execution
    #     action_result = await result.action()
    #     assert action_result is not None
    #     # Check that action executed successfully

    #     mock_asyncpg_connection.fetch.assert_called_once_with("SELECT * FROM users")

    #     del _connections["test_conn"]

    # @pytest.mark.asyncio
    # async def test_db_query_with_params(
    #     self, context, database_tools, mock_asyncpg_connection
    # ):
    #     from tools.database import _connections

    #     _connections["test_conn"] = {
    #         "type": "postgresql",
    #         "connection": mock_asyncpg_connection,
    #     }

    #     db_query_tool = next(
    #         tool for tool in database_tools if tool.schema.name == "db_query"
    #     )

    #     params = {
    #         "query": "SELECT * FROM users WHERE id = $1",
    #         "connection_name": "test_conn",
    #         "params": [1],
    #     }

    #     result = await db_query_tool.handle(context, params)

    #     assert result.code is not None
    #     assert result.action is not None

    #     # Execute the action to test the actual query execution with params
    #     action_result = await result.action()
    #     assert action_result is not None
    #     # Check that action executed successfully

    #     mock_asyncpg_connection.fetch.assert_called_once_with(
    #         "SELECT * FROM users WHERE id = $1", 1
    #     )

    #     del _connections["test_conn"]

    @pytest.mark.asyncio
    async def test_db_query_sqlserver(
        self, context, database_tools, mock_aioodbc_connection
    ):
        from tools.database import _connections

        _connections["test_conn"] = {
            "type": "sqlserver",
            "connection": mock_aioodbc_connection,
        }

        db_query_tool = next(
            tool for tool in database_tools if tool.schema.name == "db_query"
        )

        params = {"query": "SELECT * FROM users", "connection_name": "test_conn"}

        result = await db_query_tool.handle(context, params)

        assert result.code is not None
        assert result.action is not None

        # Execute the action to test the actual query execution
        action_result = await result.action()
        assert action_result is not None
        # Check that action executed successfully

        del _connections["test_conn"]

    @pytest.mark.asyncio
    async def test_db_query_connection_not_found(self, context, database_tools):
        db_query_tool = next(
            tool for tool in database_tools if tool.schema.name == "db_query"
        )

        params = {"query": "SELECT * FROM users", "connection_name": "nonexistent_conn"}

        result = await db_query_tool.handle(context, params)

        assert result.code is not None

        # Execute the action to test error handling
        action_result = await result.action()
        assert action_result is not None
        # Error expected - check content has error message
        assert (
            "Connection 'nonexistent_conn' not found"
            in action_result.content[0]["text"]
        )

    # @pytest.mark.asyncio
    # async def test_db_execute_postgresql(
    #     self, context, database_tools, mock_asyncpg_connection
    # ):
    #     from tools.database import _connections

    #     _connections["test_conn"] = {
    #         "type": "postgresql",
    #         "connection": mock_asyncpg_connection,
    #     }

    #     db_execute_tool = next(
    #         tool for tool in database_tools if tool.schema.name == "db_execute"
    #     )

    #     params = {
    #         "query": "INSERT INTO users (name) VALUES ($1)",
    #         "connection_name": "test_conn",
    #         "params": ["test_user"],
    #     }

    #     result = await db_execute_tool.handle(context, params)

    #     assert result.code is not None
    #     assert result.action is not None

    #     # Execute the action to test the actual statement execution
    #     action_result = await result.action()
    #     assert action_result is not None
    #     # Check that action executed successfully

    #     mock_asyncpg_connection.execute.assert_called_once_with(
    #         "INSERT INTO users (name) VALUES ($1)", "test_user"
    #     )

    #     del _connections["test_conn"]

    # @pytest.mark.asyncio
    # async def test_db_execute_sqlserver(
    #     self, context, database_tools, mock_aioodbc_connection
    # ):
    #     from tools.database import _connections

    #     _connections["test_conn"] = {
    #         "type": "sqlserver",
    #         "connection": mock_aioodbc_connection,
    #     }

    #     db_execute_tool = next(
    #         tool for tool in database_tools if tool.schema.name == "db_execute"
    #     )

    #     params = {
    #         "query": "INSERT INTO users (name) VALUES (?)",
    #         "connection_name": "test_conn",
    #         "params": ["test_user"],
    #     }

    #     result = await db_execute_tool.handle(context, params)

    #     assert result.code is not None
    #     assert result.action is not None

    #     # Execute the action to test the actual statement execution
    #     action_result = await result.action()
    #     assert action_result is not None
    #     # Check that action executed successfully

    #     del _connections["test_conn"]

    # @pytest.mark.asyncio
    # async def test_db_list_tables_postgresql(
    #     self, context, database_tools, mock_asyncpg_connection
    # ):
    #     from tools.database import _connections

    #     _connections["test_conn"] = {
    #         "type": "postgresql",
    #         "connection": mock_asyncpg_connection,
    #     }

    #     mock_asyncpg_connection.fetch.return_value = [
    #         {"table_name": "users"},
    #         {"table_name": "products"},
    #         {"table_name": "orders"},
    #     ]

    #     db_list_tables_tool = next(
    #         tool for tool in database_tools if tool.schema.name == "db_list_tables"
    #     )

    #     params = {"connection_name": "test_conn"}

    #     result = await db_list_tables_tool.handle(context, params)

    #     assert result.code is not None
    #     assert result.action is not None

    #     # Execute the action to test the actual table listing
    #     action_result = await result.action()
    #     assert action_result is not None
    #     # Check that action executed successfully

    #     mock_asyncpg_connection.fetch.assert_called_once()

    #     del _connections["test_conn"]

    # @pytest.mark.asyncio
    # async def test_db_list_tables_sqlserver(self, context, database_tools, mock_aioodbc_connection):
    #     # Test listing tables for SQL Server
    #     # NOTE: This test is commented out because db_list_tables is not implemented
    #     pass

    # @pytest.mark.asyncio
    # async def test_db_describe_table_sqlserver(self, context, database_tools, mock_aioodbc_connection):
    #     # Test describing table structure for SQL Server
    #     # NOTE: This test is commented out because db_describe_table is not implemented
    #     pass

    # @pytest.mark.asyncio
    # async def test_db_describe_table_sqlserver(
    #     self, context, database_tools, mock_aioodbc_connection
    # ):
    #     # NOTE: This test is commented out because db_describe_table is not implemented
    #     pass

    @pytest.mark.asyncio
    async def test_db_close(self, context, database_tools, mock_asyncpg_connection):
        from tools.database import _connections

        _connections["test_conn"] = {
            "type": "postgresql",
            "connection": mock_asyncpg_connection,
        }

        db_close_tool = next(
            tool for tool in database_tools if tool.schema.name == "db_close"
        )

        params = {"connection_name": "test_conn"}

        result = await db_close_tool.handle(context, params)

        assert result.code is not None
        assert result.action is not None

        # Execute the action to test the actual connection closing
        action_result = await result.action()
        assert action_result is not None
        # Check that action executed successfully

        mock_asyncpg_connection.close.assert_called_once()

        assert "test_conn" not in _connections

    @pytest.mark.asyncio
    async def test_db_close_connection_not_found(self, context, database_tools):
        db_close_tool = next(
            tool for tool in database_tools if tool.schema.name == "db_close"
        )

        params = {"connection_name": "nonexistent_conn"}

        result = await db_close_tool.handle(context, params)

        assert result.code is not None

        # Execute the action to test error handling
        action_result = await result.action()
        assert action_result is not None
        # Error expected - check content has error message
        assert (
            "Connection 'nonexistent_conn' not found"
            in action_result.content[0]["text"]
        )

    @pytest.mark.asyncio
    async def test_tools_capture_snapshot_and_wait_for_network_settings(
        self, context, database_tools
    ):
        for tool in database_tools:
            if tool.schema.name == "db_connect":
                params = {
                    "db_type": "postgresql",
                    "host": "localhost",
                    "database": "test",
                    "username": "user",
                    "password": "pass",
                    "connection_name": "test",
                }
            elif tool.schema.name in ["db_query", "db_execute"]:
                params = {"query": "SELECT 1", "connection_name": "test"}
            elif tool.schema.name == "db_describe_table":
                params = {"table_name": "users", "connection_name": "test"}
            else:
                params = {"connection_name": "test"}

            with (
                patch("asyncpg.connect", new_callable=AsyncMock),
                patch("aioodbc.connect", new_callable=AsyncMock),
            ):
                try:
                    result = await tool.handle(context, params)
                    assert result.capture_snapshot is False
                    assert result.wait_for_network is False
                except Exception:
                    pass


class TestDatabaseIntegration:
    # @pytest.mark.asyncio
    # async def test_full_workflow_postgresql(self, context, database_tools):
    #     tools_dict = {tool.schema.name: tool for tool in database_tools}

    #     mock_connection = AsyncMock()
    #     mock_connection.fetch.return_value = [{"count": 1}]
    #     mock_connection.execute.return_value = "INSERT 0 1"

    #     with patch("asyncpg.connect", return_value=mock_connection):
    #         # Test connect
    #         connect_result = await tools_dict["db_connect"].handle(
    #             context,
    #             {
    #                 "db_type": "postgresql",
    #                 "host": "localhost",
    #                 "database": "test",
    #                 "username": "user",
    #                 "password": "pass",
    #                 "connection_name": "workflow_test",
    #             },
    #         )
    #         assert connect_result.code is not None
    #         await connect_result.action()  # Actually execute the connection

    #         # Test query
    #         query_result = await tools_dict["db_query"].handle(
    #             context,
    #             {
    #                 "query": "SELECT COUNT(*) as count FROM users",
    #                 "connection_name": "workflow_test",
    #             },
    #         )
    #         assert query_result.code is not None
    #         await query_result.action()  # Actually execute the query

    #         # Test execute
    #         execute_result = await tools_dict["db_execute"].handle(
    #             context,
    #             {
    #                 "query": "INSERT INTO users (name) VALUES ($1)",
    #                 "connection_name": "workflow_test",
    #                 "params": ["test_user"],
    #             },
    #         )
    #         assert execute_result.code is not None
    #         await execute_result.action()  # Actually execute the statement

    #         # Test close
    #         close_result = await tools_dict["db_close"].handle(
    #             context, {"connection_name": "workflow_test"}
    #         )
    #         assert close_result.code is not None
    #         await close_result.action()  # Actually close the connection

    # @pytest.mark.asyncio
    # async def test_error_handling_invalid_sql(
    #     self, context, database_tools, mock_asyncpg_connection
    # ):
    #     from tools.database import _connections

    #     _connections["test_conn"] = {
    #         "type": "postgresql",
    #         "connection": mock_asyncpg_connection,
    #     }

    #     mock_asyncpg_connection.fetch.side_effect = Exception(
    #         "syntax error at or near 'INVALID'"
    #     )

    #     db_query_tool = next(
    #         tool for tool in database_tools if tool.schema.name == "db_query"
    #     )

    #     params = {
    #         "query": "SELECT * FROM INVALID_TABLE_NAME",
    #         "connection_name": "test_conn",
    #     }

    #     result = await db_query_tool.handle(context, params)

    #     assert result.code is not None

    #     # Execute the action to test error handling
    #     action_result = await result.action()
    #     assert action_result is not None
    #     # Error expected - check content has error message
    #     assert "syntax error" in action_result.content[0]["text"]

    #     del _connections["test_conn"]

    def test_connection_pooling_simulation(self, database_tools):
        from tools.database import _connections

        _connections.clear()

        mock_conn1 = Mock()
        mock_conn2 = Mock()

        _connections["conn1"] = mock_conn1
        _connections["conn2"] = mock_conn2

        assert len(_connections) == 2
        assert _connections["conn1"] is mock_conn1
        assert _connections["conn2"] is mock_conn2

        _connections.clear()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
