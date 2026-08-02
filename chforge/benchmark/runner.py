"""
Benchmark Runner - Execute queries with multiple configurations
"""

import time
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field

from ..client.clickhouse_client import ClickHouseClient
from ..executor.query_executor import QueryExecutor, QueryResult
from ..resources.config import ResourceConfig
from ..utils.logger import logger


@dataclass
class BenchmarkResult:
    """Result of a benchmark run"""
    query: str
    configs: List[ResourceConfig]
    results: List[QueryResult]
    total_time: float
    iterations_per_config: int
    timestamp: float = field(default_factory=time.time)

    @property
    def success_count(self) -> int:
        return sum(1 for r in self.results if r.success)

    @property
    def failure_count(self) -> int:
        return len(self.results) - self.success_count

    def to_table(self) -> str:
        """Generate a formatted table of results"""
        from tabulate import tabulate

        headers = ["Threads", "Memory", "Time (s)", "Rows", "Read MB", "Status"]
        table = []
        for r in self.results:
            table.append([
                r.config.threads or "-",
                r.config.memory or "-",
                f"{r.execution_time:.3f}",
                r.rows_returned,
                f"{r.read_mb:.2f}",
                "✅" if r.success else f"❌ {r.error[:30]}" if r.error else "❌"
            ])
        return tabulate(table, headers=headers, tablefmt="grid")


class BenchmarkRunner:
    """Run benchmarks with multiple configurations"""

    def __init__(self, client: ClickHouseClient):
        self.client = client
        self.executor = QueryExecutor(client)

    def run(
            self,
            sql: str,
            configs: List[ResourceConfig],
            iterations: int = 3,
            warmup: int = 1,
            parameters: Optional[Dict] = None,
    ) -> BenchmarkResult:
        """
        Run a benchmark with multiple configurations

        Args:
            sql: SQL query string
            configs: List of resource configurations
            iterations: Number of times to run each config
            warmup: Number of warmup runs (results discarded)
            parameters: Query parameters

        Returns:
            BenchmarkResult with all results
        """
        logger.info(f"Running benchmark with {len(configs)} configs, {iterations} iterations each")

        start_time = time.time()
        all_results = []

        for idx, config in enumerate(configs, 1):
            logger.info(f"Config {idx}/{len(configs)}: {config}")

            # Warmup runs
            for _ in range(warmup):
                self.executor.execute(sql, config, parameters)

            # Benchmark runs
            for run_num in range(iterations):
                logger.debug(f"  Run {run_num + 1}/{iterations}")
                result = self.executor.execute(sql, config, parameters)
                all_results.append(result)

        total_time = time.time() - start_time

        return BenchmarkResult(
            query=sql,
            configs=configs,
            results=all_results,
            total_time=total_time,
            iterations_per_config=iterations,
        )

    def run_quick(
            self,
            sql: str,
            configs: List[ResourceConfig],
    ) -> BenchmarkResult:
        """Quick benchmark (1 iteration, no warmup)"""
        return self.run(sql, configs, iterations=1, warmup=0)