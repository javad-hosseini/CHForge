"""
Test script for Auto Resource Optimizer
"""

from chforge.client import ClickHouseClient
from chforge.resources import ResourceConfig
from chforge.benchmark import BenchmarkRunner
from chforge.benchmark.optimizer import ResourceOptimizer


def main():
    # Connect
    client = ClickHouseClient(
        host="192.168.247.128",
        port=8123,
        database="telecom_analytics",
        username="default",
        password="",
    )

    # Query (slightly heavier)
    sql = """
        SELECT 
            city, 
            count() as total,
            avg(latency_ms) as avg_latency
        FROM network_events 
        WHERE event_time > now() - INTERVAL 30 DAY
        GROUP BY city 
        ORDER BY total DESC 
        LIMIT 10
    """

    # Manual config
    manual_config = ResourceConfig(threads=4, memory="4G")

    # Run optimizer
    runner = BenchmarkRunner(client)
    optimizer = ResourceOptimizer(client, runner)

    print("\n" + "=" * 60)
    print("OPTIMIZER TEST")
    print("=" * 60)

    # Test 1: Optimize a query
    print("\n1. OPTIMIZING QUERY...")
    result = optimizer.optimize(
        sql=sql,
        objective="time",
        iterations=2,
        warmup=1,
    )

    print("\n2. OPTIMIZATION RESULT:")
    print("=" * 60)
    print(f"Best config: {result.best_config}")
    print(f"Best time: {result.best_time:.4f}s")
    print(f"Configs tested: {result.configs_tested}")
    print(f"Success rate: {result.success_rate:.0%}")
    print("\nRecommendation:")
    print(result.recommendation)

    # Test 2: Compare manual vs auto
    print("\n" + "=" * 60)
    print("3. MANUAL VS AUTO COMPARISON")
    print("=" * 60)

    comparison = optimizer.compare_manual_vs_auto(
        sql=sql,
        manual_config=manual_config,
        iterations=2,
    )

    print(f"\nManual config: {comparison['manual']['config']}")
    print(f"Manual time: {comparison['manual']['avg_time']:.4f}s")
    print(f"\nAuto config: {comparison['auto']['config']}")
    print(f"Auto time: {comparison['auto']['avg_time']:.4f}s")
    print(f"\nImprovement: {comparison['improvement_percent']:.1f}%")
    print(f"Recommendation: Use {comparison['recommendation']}")
    print(f"Analysis: {comparison['analysis']}")

    client.close()


if __name__ == "__main__":
    main()