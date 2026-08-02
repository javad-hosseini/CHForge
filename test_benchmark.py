"""
Test script for Benchmark Runner
"""

from chforge.client import ClickHouseClient
from chforge.resources import ResourceConfig, ResourceManager
from chforge.benchmark import BenchmarkRunner


def main():
    # Connect to ClickHouse
    client = ClickHouseClient(
        host="192.168.247.128",
        port=8123,
        database="telecom_analytics",
        username="default",
        password="",
    )

    # Define query (simple aggregation)
    sql = "SELECT city, count() FROM network_events GROUP BY city LIMIT 10"

    # Define configs
    configs = [
        ResourceConfig(threads=2),
        ResourceConfig(threads=4),
        ResourceConfig(threads=8),
    ]

    # Run benchmark
    print("\n" + "=" * 60)
    print("RUNNING BENCHMARK...")
    print("=" * 60)

    runner = BenchmarkRunner(client)
    result = runner.run_quick(sql, configs)

    # Print results
    print("\n" + "=" * 60)
    print("BENCHMARK RESULTS")
    print("=" * 60)

    # Use to_table without Unicode
    from tabulate import tabulate
    headers = ["Threads", "Memory", "Time (s)", "Rows", "Read MB", "Status"]
    table = []
    for r in result.results:
        status = "OK" if r.success else f"ERR"
        table.append([
            r.config.threads or "-",
            r.config.memory or "-",
            f"{r.execution_time:.3f}",
            r.rows_returned,
            f"{r.read_mb:.2f}",
            status
        ])
    print(tabulate(table, headers=headers, tablefmt="grid"))

    print(f"\nSuccess: {result.success_count}/{len(result.results)}")
    print(f"Failures: {result.failure_count}")
    print(f"Total time: {result.total_time:.2f}s")

    client.close()


if __name__ == "__main__":
    main()