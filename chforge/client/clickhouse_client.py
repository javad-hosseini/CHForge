"""
ClickHouse Client - Connection and query execution
"""

import clickhouse_connect
from typing import Optional, Dict, Any
from ..utils.logger import logger


class ClickHouseClient:
    """ClickHouse client wrapper with connection management"""

    def __init__(
        self,
        host: str,
        port: int = 8123,
        database: str = "default",
        username: str = "default",
        password: str = "",
        connect_timeout: int = 30,
        send_receive_timeout: int = 300,
    ):
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.password = password
        self.connect_timeout = connect_timeout
        self.send_receive_timeout = send_receive_timeout

        self._client: Optional[clickhouse_connect.driver.Client] = None
        self._connect()

    def _connect(self) -> None:
        """Establish connection to ClickHouse"""
        try:
            logger.info(f"Connecting to ClickHouse at {self.host}:{self.port}")
            self._client = clickhouse_connect.get_client(
                host=self.host,
                port=self.port,
                database=self.database,
                username=self.username,
                password=self.password,
                connect_timeout=self.connect_timeout,
                send_receive_timeout=self.send_receive_timeout,
            )
            version = self._client.query("SELECT version()").result_rows[0][0]
            logger.info(f"Connected! Version: {version}")
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            raise

    def query(
        self,
        sql: str,
        parameters: Optional[Dict] = None,
        settings: Optional[Dict] = None,
    ) -> Any:
        """
        Execute a query with optional parameters and settings

        Args:
            sql: SQL query string
            parameters: Query parameters (for parameterized queries)
            settings: ClickHouse settings to apply

        Returns:
            Query result object with .result_rows and .summary
        """
        try:
            if settings:
                result = self._client.query(sql, parameters=parameters, settings=settings)
            else:
                result = self._client.query(sql, parameters=parameters)
            return result
        except Exception as e:
            logger.error(f"Query failed: {e}")
            logger.error(f"SQL: {sql[:200]}...")
            raise

    @property
    def client(self):
        return self._client

    def close(self) -> None:
        if self._client:
            self._client.close()
            logger.info("Connection closed")