#!/usr/bin/env python
"""
CHForge - ClickHouse Performance Benchmark Framework
Usage:
    python run.py --query heavy_agg --profile standard
    python run.py --query light_agg --profile quick --iterations 5
    python run.py --optimize --query heavy_agg --objective memory
"""

import argparse
import sys
from pathlib import Path

from chforge.client import ClickHouseClient
from chforge.resources import ResourceConfig, ResourceManager
from chforge.benchmark import BenchmarkRunner, ResourceOptimizer
from chforge.config.loader import ConfigLoader


def main():
    parser = argparse.ArgumentParser(
        description="CHForge - ClickHouse Performance Benchmark"
    )

    # Query and profile selection
    parser.add_argument(
        "--query", "-q",
        required=True,
        help="Query name from queries.yaml (e.g., heavy_agg, light_agg)"
    )
    parser.add_argument(
        "--profile", "-p",
        default="standard",
        help="Profile name from profiles.yaml (default: standard)"
    )

    # Benchmark settings
    parser.add_argument(
        "--iterations", "-i",
        type=int,
        help="Number of iterations per config (overrides config.yaml)"
    )
    parser.add_argument(
        "--warmup", "-w",
        type=int,
        help="Number of warmup runs (overrides config.yaml)"
    )

    # Mode selection
    parser.add_argument(
        "--optimize", "-o",
        action="store_true",
        help="Run optimizer instead of benchmark"
    )
    parser.add_argument(
        "--objective",
        choices=["time", "memory"],
        help="Optimization objective (time or memory)"
    )

    # Connection override
    parser.add_argument(
        "--host",
        help="Override ClickHouse host"
    )
    parser.add_argument(
        "--database",
        help="Override ClickHouse database"
    )

    args = parser.parse_args()

    # Load configuration
    loader = ConfigLoader()

    # Get connection settings
    ch_config = loader.get_clickhouse_config()
    if args.host:
        ch_config["host"] = args.host
    if args.database:
        ch_config["database"] = args.database

    # Get query
    sql = loader.get_query(args.query)

    # Get profile
    profile_configs = loader.get_profile(args.profile)

    # Convert to ResourceConfig objects
    configs = [ResourceConfig(**cfg) for cfg in profile_configs]

    # Get benchmark defaults
    bench_config = loader.get_benchmark_config()
    iterations = args.iterations or bench_config.get("default_iterations", 3)
    warmup = args.warmup or bench_config.get("default_warmup", 1)
    objective = args.objective or bench_config.get("default_objective", "time")

    # Connect to ClickHouse
    client = ClickHouseClient(
        host=ch_config["host"],
        port=ch_config["port"],
        database=ch_config["database"],
        username=ch_config["username"],
        password=ch_config["password"],
    )

    runner = BenchmarkRunner(client)

    print("\n" + "=" * 60)
    print(f"📊 Query: {args.query}")
    print(f"📋 Profile: {args.profile} ({len(configs)} configs)")
    print(f"🔄 Iterations: {iterations}, Warmup: {warmup}")
    print("=" * 60)

    try:
        if args.optimize:
            # Run optimizer
            optimizer = ResourceOptimizer(client, runner)
            result = optimizer.optimize(
                sql=sql,
                objective=objective,
                iterations=iterations,
                warmup=warmup,
            )

            print("\n🏆 OPTIMIZATION RESULT:")
            print("=" * 60)
            print(f"Best config: {result.best_config}")
            print(f"Best time: {result.best_time:.4f}s")
            print(f"Configs tested: {result.configs_tested}")
            print(f"Success rate: {result.success_rate:.0%}")
            print("\nRecommendation:")
            print(result.recommendation)
        else:
            # Run benchmark
            benchmark_result = runner.run(
                sql=sql,
                configs=configs,
                iterations=iterations,
                warmup=warmup,
            )

            print("\n📊 BENCHMARK RESULTS:")
            print("=" * 60)
            print(benchmark_result.to_table())

            print(f"\n✅ Success: {benchmark_result.success_count}/{len(benchmark_result.results)}")
            print(f"❌ Failures: {benchmark_result.failure_count}")
            print(f"⏱️  Total time: {benchmark_result.total_time:.2f}s")

    finally:
        client.close()


if __name__ == "__main__":
    main()