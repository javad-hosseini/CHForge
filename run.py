#!/usr/bin/env python
"""
CHForge - ClickHouse Performance Benchmark Framework

Usage:
    python run.py --query heavy_agg --profile standard
    python run.py --query light_agg --profile quick --iterations 5
    python run.py --optimize --query heavy_agg --objective memory
    python run.py --list-queries
    python run.py --list-profiles
    python run.py --system-info
    python run.py --clickhouse-info
"""

import argparse
import sys
from pathlib import Path

from chforge.client import ClickHouseClient
from chforge.resources import ResourceConfig
from chforge.benchmark import BenchmarkRunner
from chforge.benchmark.optimizer import ResourceOptimizer
from chforge.config.loader import ConfigLoader
from chforge.system import print_system_info, get_system_info
from chforge.system.clickhouse_info import ClickHouseInfoCollector
from chforge.utils.logger import logger


def main():
    parser = argparse.ArgumentParser(
        description="CHForge - ClickHouse Performance Benchmark Framework"
    )

    # Query and profile selection
    parser.add_argument(
        "--query", "-q",
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

    # List commands
    parser.add_argument(
        "--list-queries",
        action="store_true",
        help="List all available queries"
    )
    parser.add_argument(
        "--list-profiles",
        action="store_true",
        help="List all available profiles"
    )

    # System info (local)
    parser.add_argument(
        "--system-info",
        action="store_true",
        help="Show local system information and exit"
    )

    # ClickHouse server info (remote)
    parser.add_argument(
        "--clickhouse-info",
        action="store_true",
        help="Show ClickHouse server system information and exit"
    )

    args = parser.parse_args()

    # Handle local system info
    if args.system_info:
        print_system_info()
        return

    # Handle ClickHouse server info
    if args.clickhouse_info:
        loader = ConfigLoader()
        ch_config = loader.get_clickhouse_config()

        try:
            client = ClickHouseClient(
                host=ch_config["host"],
                port=ch_config["port"],
                database=ch_config["database"],
                username=ch_config["username"],
                password=ch_config["password"],
            )
            collector = ClickHouseInfoCollector(client)
            collector.print_summary()
            client.close()
        except Exception as e:
            print(f"❌ Failed to get ClickHouse server info: {e}")
            sys.exit(1)
        return

    # Load configuration
    loader = ConfigLoader()

    # Handle list commands
    if args.list_queries:
        print("\n📋 Available Queries:")
        print("-" * 40)
        for q in loader.list_queries():
            desc = loader.get_query_description(q)
            print(f"  {q}: {desc}")
        print("-" * 40)
        return

    if args.list_profiles:
        print("\n📋 Available Profiles:")
        print("-" * 40)
        for p in loader.list_profiles():
            desc = loader.get_profile_description(p)
            print(f"  {p}: {desc}")
        print("-" * 40)
        return

    # Validate required arguments
    if not args.query:
        print("❌ Error: --query is required")
        print("Use --list-queries to see available queries")
        sys.exit(1)

    # Get connection settings
    ch_config = loader.get_clickhouse_config()
    if args.host:
        ch_config["host"] = args.host
    if args.database:
        ch_config["database"] = args.database

    # Get query
    try:
        sql = loader.get_query(args.query)
        query_description = loader.get_query_description(args.query)
    except ValueError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

    # Get profile
    try:
        profile_configs = loader.get_profile(args.profile)
        profile_description = loader.get_profile_description(args.profile)
    except ValueError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

    # Convert to ResourceConfig objects
    configs = [ResourceConfig(**cfg) for cfg in profile_configs]

    # Get benchmark defaults
    bench_config = loader.get_benchmark_config()
    iterations = args.iterations or bench_config.get("default_iterations", 3)
    warmup = args.warmup or bench_config.get("default_warmup", 1)
    objective = args.objective or bench_config.get("default_objective", "time")

    # Print header
    print("\n" + "=" * 60)
    print(f"📊 CHForge Benchmark")
    print("=" * 60)
    print(f"📌 Query: {args.query} - {query_description}")
    print(f"📋 Profile: {args.profile} - {profile_description}")
    print(f"⚙️  Configs: {len(configs)}")
    print(f"🔄 Iterations: {iterations}, Warmup: {warmup}")
    if args.optimize:
        print(f"🎯 Objective: {objective}")
    print("=" * 60)

    # Connect to ClickHouse
    try:
        client = ClickHouseClient(
            host=ch_config["host"],
            port=ch_config["port"],
            database=ch_config["database"],
            username=ch_config["username"],
            password=ch_config["password"],
        )
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        sys.exit(1)

    runner = BenchmarkRunner(client)

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
            print("\n💡 Recommendation:")
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