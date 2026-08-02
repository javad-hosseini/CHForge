"""
Query Executor - Execute queries and collect metrics
"""

import time
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List

from ..client.clickhouse_client import ClickHouseClient
from ..resources.config import ResourceConfig
from ..utils.logger import logger


@dataclass
class QueryResult:
    """Result of a single query execution"""
    query: str
    config: ResourceConfig
    settings: Dict[str, Any]
    execution_time: float
    rows_returned: int
    read_rows: int
    read_bytes: int
    memory_usage: Optional[int] = None
    error: Optional[str] = None
    result: Any = None
    timestamp: float = field(default_factory=time.time)

    @property
    def success(self) -> bool:
        return self.error is None

    @property
    def read_mb(self) -> float:
        """Convert read_bytes to MB, handling both int and str"""
        if self.read_bytes is None or self.read_bytes == 0:
            return 0.0
        try:
            # If it's a string like "123456", convert to int
            if isinstance(self.read_bytes, str):
                return float(self.read_bytes) / (1024 * 1024)
            return self.read_bytes / (1024 * 1024)
        except (ValueError, TypeError):
            return 0.0

    @property
    def memory_mb(self) -> float:
        if self.memory_usage is None or self.memory_usage == 0:
            return 0.0
        try:
            if isinstance(self.memory_usage, str):
                return float(self.memory_usage) / (1024 * 1024)
            return self.memory_usage / (1024 * 1024)
        except (ValueError, TypeError):
            return 0.0


class QueryExecutor:
    """Executes queries and collects performance metrics"""

    def __init__(self, client: ClickHouseClient):
        self.client = client

    def execute(
        self,
        sql: str,
        config: Optional[ResourceConfig] = None,
        parameters: Optional[Dict] = None,
    ) -> QueryResult:
        """
        Execute a query with the given resource configuration
        """
        settings = config.to_dict() if config else {}

        start_time = time.perf_counter()

        try:
            result = self.client.query(sql, parameters=parameters, settings=settings)
            elapsed = time.perf_counter() - start_time

            # Extract metrics from result summary
            summary = result.summary if hasattr(result, 'summary') else {}

            # Helper to safely convert values to int
            def safe_int(value):
                if value is None:
                    return 0
                try:
                    return int(value)
                except (ValueError, TypeError):
                    return 0

            return QueryResult(
                query=sql,
                config=config if config else ResourceConfig(),
                settings=settings,
                execution_time=elapsed,
                rows_returned=len(result.result_rows) if result.result_rows else 0,
                read_rows=safe_int(summary.get('read_rows', 0)),
                read_bytes=safe_int(summary.get('read_bytes', 0)),
                memory_usage=safe_int(summary.get('memory_usage')) if summary.get('memory_usage') else None,
                result=result,
            )
        except Exception as e:
            elapsed = time.perf_counter() - start_time
            error_msg = str(e)
            logger.error(f"Query execution failed: {error_msg}")

            return QueryResult(
                query=sql,
                config=config if config else ResourceConfig(),
                settings=settings,
                execution_time=elapsed,
                rows_returned=0,
                read_rows=0,
                read_bytes=0,
                error=error_msg,
            )