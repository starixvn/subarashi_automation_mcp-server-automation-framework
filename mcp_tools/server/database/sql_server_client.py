"""
SQL Server client for database operations.
"""

import logging
import pyodbc
from typing import List, Dict, Any, Optional, Union

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SQLServerClient:
    """
    SQL Server client that provides methods for querying and manipulating SQL Server databases.
    """

    def __init__(
        self,
        server: str,
        database: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        trusted_connection: bool = False,
        connection_string: Optional[str] = None,
    ):
        """
        Initialize the SQL Server client.

        Args:
            server: SQL Server instance name/address
            database: Database name
            username: SQL Server username (if not using trusted connection)
            password: SQL Server password (if not using trusted connection)
            trusted_connection: Whether to use Windows authentication
            connection_string: Optional custom connection string (overrides other parameters)
        """
        self.server = server
        self.database = database
        self.username = username
        self.password = password
        self.trusted_connection = trusted_connection
        self.custom_connection_string = connection_string
        self.connection = None

        logger.info(
            f"Initialized SQL Server client for database '{database}' on server '{server}'"
        )

    def _get_connection_string(self) -> str:
        """
        Build the connection string based on provided parameters.

        Returns:
            SQL Server connection string
        """
        if self.custom_connection_string:
            return self.custom_connection_string

        if self.trusted_connection:
            return f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={self.server};DATABASE={self.database};Trusted_Connection=yes;"
        else:
            return f"DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={self.server};DATABASE={self.database};UID={self.username};PWD={self.password};"

    def _ensure_connection(self) -> bool:
        """
        Ensure that a database connection exists and is valid.

        Returns:
            True if connection is established, False otherwise
        """
        try:
            if self.connection is None:
                connection_string = self._get_connection_string()
                self.connection = pyodbc.connect(connection_string)
                logger.info(
                    f"Connected to database '{self.database}' on server '{self.server}'"
                )

            # Test if connection is still valid
            cursor = self.connection.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            return True
        except Exception as e:
            logger.error(f"Connection error: {str(e)}")
            self.connection = None
            return False

    def test_connection(self) -> bool:
        """
        Test the database connection.

        Returns:
            True if connection is successful, False otherwise
        """
        try:
            return self._ensure_connection()
        except Exception as e:
            logger.error(f"Test connection failed: {str(e)}")
            return False

    def execute_query(
        self, query: str, params: Optional[List[Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute a SELECT query and return results as a list of dictionaries.

        Args:
            query: SQL query to execute
            params: Optional parameters for the query

        Returns:
            List of dictionaries with query results
        """
        if not self._ensure_connection():
            logger.error("Cannot execute query - not connected to database")
            return []

        try:
            cursor = self.connection.cursor()

            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            # Get column names
            columns = [column[0] for column in cursor.description]

            # Convert to list of dictionaries
            results = []
            for row in cursor.fetchall():
                results.append({columns[i]: row[i] for i in range(len(columns))})

            cursor.close()
            return results
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            logger.error(f"Query: {query}")
            if params:
                logger.error(f"Parameters: {params}")
            return []

    def execute_non_query(self, query: str, params: Optional[List[Any]] = None) -> int:
        """
        Execute a non-query SQL statement (INSERT, UPDATE, DELETE).

        Args:
            query: SQL statement to execute
            params: Optional parameters for the statement

        Returns:
            Number of rows affected, or -1 if an error occurred
        """
        if not self._ensure_connection():
            logger.error("Cannot execute non-query - not connected to database")
            return -1

        try:
            cursor = self.connection.cursor()

            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            affected = cursor.rowcount
            self.connection.commit()
            cursor.close()
            return affected
        except Exception as e:
            logger.error(f"Error executing non-query: {str(e)}")
            logger.error(f"Query: {query}")
            if params:
                logger.error(f"Parameters: {params}")

            try:
                self.connection.rollback()
            except Exception as rollback_err:
                logger.error(f"Error during rollback: {str(rollback_err)}")

            return -1

    def execute_many(self, query: str, params_list: List[List[Any]]) -> int:
        """
        Execute the same SQL statement with multiple parameter sets.

        Args:
            query: SQL statement to execute
            params_list: List of parameter sets

        Returns:
            Total number of rows affected, or -1 if an error occurred
        """
        if not self._ensure_connection():
            logger.error("Cannot execute batch - not connected to database")
            return -1

        if not params_list:
            logger.error("No parameter sets provided for batch execution")
            return 0

        try:
            cursor = self.connection.cursor()

            cursor.executemany(query, params_list)
            affected = cursor.rowcount
            self.connection.commit()
            cursor.close()
            return affected
        except Exception as e:
            logger.error(f"Error executing batch: {str(e)}")
            logger.error(f"Query: {query}")
            logger.error(f"Parameter sets count: {len(params_list)}")

            try:
                self.connection.rollback()
            except Exception as rollback_err:
                logger.error(f"Error during rollback: {str(rollback_err)}")

            return -1

    def execute_script(self, script: str) -> bool:
        """
        Execute a multi-statement SQL script.

        Args:
            script: SQL script to execute

        Returns:
            True if execution was successful, False otherwise
        """
        if not self._ensure_connection():
            logger.error("Cannot execute script - not connected to database")
            return False

        try:
            cursor = self.connection.cursor()

            # Split script by GO statements (common SQL Server batch separator)
            # This is a simple implementation and might not handle all edge cases
            batches = script.split("GO")

            for batch in batches:
                if batch.strip():  # Only execute non-empty batches
                    cursor.execute(batch)

            self.connection.commit()
            cursor.close()
            return True
        except Exception as e:
            logger.error(f"Error executing script: {str(e)}")

            try:
                self.connection.rollback()
            except Exception as rollback_err:
                logger.error(f"Error during rollback: {str(rollback_err)}")

            return False

    def get_tables(self) -> List[str]:
        """
        Get a list of tables in the connected database.

        Returns:
            List of table names
        """
        query = """
        SELECT TABLE_NAME 
        FROM INFORMATION_SCHEMA.TABLES 
        WHERE TABLE_TYPE = 'BASE TABLE' 
        ORDER BY TABLE_NAME
        """

        try:
            results = self.execute_query(query)
            return [row["TABLE_NAME"] for row in results]
        except Exception as e:
            logger.error(f"Error getting tables: {str(e)}")
            return []

    def get_columns(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Get column information for a table.

        Args:
            table_name: Name of the table

        Returns:
            List of column information dictionaries
        """
        query = """
        SELECT 
            COLUMN_NAME, 
            DATA_TYPE, 
            CHARACTER_MAXIMUM_LENGTH,
            IS_NULLABLE, 
            COLUMN_DEFAULT
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_NAME = ?
        ORDER BY ORDINAL_POSITION
        """

        try:
            return self.execute_query(query, [table_name])
        except Exception as e:
            logger.error(f"Error getting columns for table '{table_name}': {str(e)}")
            return []

    def close(self) -> None:
        """
        Close the database connection.
        """
        if self.connection:
            try:
                self.connection.close()
                logger.info(
                    f"Closed connection to database '{self.database}' on server '{self.server}'"
                )
            except Exception as e:
                logger.error(f"Error closing connection: {str(e)}")
            finally:
                self.connection = None
