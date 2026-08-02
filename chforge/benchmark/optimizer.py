"""
Auto Resource Optimizer - Find the best configuration automatically
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
import time

from .runner import BenchmarkRunner, BenchmarkResult
from ..resources.config import ResourceConfig
from ..resources.manager import ResourceManager
from ..utils.logger import logger


@dataclass
class OptimizationResult:
    """Result of auto optimization"""
    query: str
    best_config: ResourceConfig
    best_time: float
    all_results: List[Dict[str, Any]]
    configs_tested: int
    success_rate: float
    recommendation: str


class ResourceOptimizer:
    """Automatically find the best resource configuration for a query"""

    def __init__(self, client, benchmark_runner: BenchmarkRunner):
        self.client = client
        self.runner = benchmark_runner

    def optimize(
            self,
            sql: str,
            search_space: Optional[List[ResourceConfig]] = None,
            objective: str = "time",  # "time" or "memory"
            iterations: int = 2,
            warmup: int = 1,
            parameters: Optional[Dict] = None,
    ) -> OptimizationResult:
        """
        Find the best configuration for a query

        Args:
            sql: SQL query
            search_space: List of configs to try (if None, uses default)
            objective: "time" or "memory" - what to optimize for
            iterations: Number of iterations per config
            warmup: Number of warmup runs
            parameters: Query parameters

        Returns:
            OptimizationResult with best config and analysis
        """

        # Generate search space if not provided
        if search_space is None:
            search_space = self._generate_search_space()

        logger.info(f"Optimizing query with {len(search_space)} configurations...")
        logger.info(f"Objective: minimize {objective}")

        results = []

        for config in search_space:
            logger.debug(f"Testing: {config}")

            # Run benchmark for this config
            benchmark_result = self.runner.run(
                sql=sql,
                configs=[config],
                iterations=iterations,
                warmup=warmup,
                parameters=parameters,
            )

            # Extract metrics
            if benchmark_result.results:
                avg_time = sum(r.execution_time for r in benchmark_result.results) / len(benchmark_result.results)
                avg_memory = sum(r.memory_mb for r in benchmark_result.results if r.memory_mb) / len(
                    benchmark_result.results) if benchmark_result.results else 0
                success = benchmark_result.success_count > 0
            else:
                avg_time = float('inf')
                avg_memory = float('inf')
                success = False

            results.append({
                "config": config,
                "avg_time": avg_time,
                "avg_memory": avg_memory,
                "success": success,
                "iterations": benchmark_result.success_count,
                "total_runs": len(benchmark_result.results),
            })

            logger.debug(f"  Time: {avg_time:.4f}s, Memory: {avg_memory:.2f}MB")

        # Find best configuration
        best_config = self._find_best(results, objective)

        # Generate recommendation
        recommendation = self._generate_recommendation(results, best_config, objective)

        return OptimizationResult(
            query=sql,
            best_config=best_config,
            best_time=min(r["avg_time"] for r in results if r["success"]),
            all_results=results,
            configs_tested=len(results),
            success_rate=sum(1 for r in results if r["success"]) / len(results),
            recommendation=recommendation,
        )

    def _generate_search_space(self) -> List[ResourceConfig]:
        """Generate default search space for optimization"""
        configs = []

        # Thread profiles
        threads = [2, 4, 8, 16]
        memory = ["2G", "4G", "8G"]

        for t in threads:
            configs.append(ResourceConfig(threads=t))

        for t in threads[:2]:  # Test fewer threads with memory
            for m in memory:
                configs.append(ResourceConfig(threads=t, memory=m))

        return configs

    def _find_best(
            self,
            results: List[Dict[str, Any]],
            objective: str
    ) -> ResourceConfig:
        """Find best config based on objective"""
        valid_results = [r for r in results if r["success"]]

        if not valid_results:
            logger.warning("No successful runs! Returning first config.")
            return results[0]["config"]

        if objective == "time":
            best = min(valid_results, key=lambda x: x["avg_time"])
        elif objective == "memory":
            best = min(valid_results, key=lambda x: x["avg_memory"])
        else:
            best = min(valid_results, key=lambda x: x["avg_time"])

        return best["config"]

    def _generate_recommendation(
            self,
            results: List[Dict[str, Any]],
            best: ResourceConfig,
            objective: str
    ) -> str:
        """Generate human-readable recommendation"""

        best_time = min(r["avg_time"] for r in results if r["success"])
        worst_time = max(r["avg_time"] for r in results if r["success"])

        # Find worst config for comparison
        worst = max(results, key=lambda x: x["avg_time"]) if results else None

        if worst and best_time > 0:
            improvement = ((worst["avg_time"] - best_time) / worst["avg_time"]) * 100
        else:
            improvement = 0

        lines = []
        lines.append(f"Objective: Minimize {objective}")
        lines.append(f"Best config: {best}")
        lines.append(f"Best time: {best_time:.4f}s")

        if improvement > 0:
            lines.append(f"Improvement: {improvement:.1f}% faster than worst config")

        lines.append(f"Success rate: {sum(1 for r in results if r['success'])}/{len(results)}")

        # Suggest next steps
        if objective == "time" and best.threads and best.threads >= 16:
            lines.append("Tip: Your query scales well with threads!")
        elif objective == "time" and best.threads and best.threads <= 4:
            lines.append("Tip: Your query may be I/O or memory bound.")

        return "\n".join(lines)

    def compare_manual_vs_auto(
            self,
            sql: str,
            manual_config: ResourceConfig,
            search_space: Optional[List[ResourceConfig]] = None,
            iterations: int = 2,
    ) -> Dict[str, Any]:
        """
        Compare manual configuration vs auto-optimized configuration

        Returns:
            Dict with comparison results
        """
        # Run manual
        logger.info("Running manual configuration...")
        manual_result = self.runner.run(
            sql=sql,
            configs=[manual_config],
            iterations=iterations,
            warmup=1,
        )
        manual_time = sum(r.execution_time for r in manual_result.results) / len(manual_result.results)

        # Run auto optimization
        logger.info("Running auto optimization...")
        auto_opt = self.optimize(sql, search_space, objective="time", iterations=iterations)

        # Run auto optimized config
        auto_result = self.runner.run(
            sql=sql,
            configs=[auto_opt.best_config],
            iterations=iterations,
            warmup=1,
        )
        auto_time = sum(r.execution_time for r in auto_result.results) / len(auto_result.results)

        improvement = ((manual_time - auto_time) / manual_time) * 100 if manual_time > 0 else 0

        return {
            "manual": {
                "config": manual_config,
                "avg_time": manual_time,
            },
            "auto": {
                "config": auto_opt.best_config,
                "avg_time": auto_time,
            },
            "improvement_percent": improvement,
            "recommendation": "Auto" if improvement > 5 else "Manual",
            "analysis": f"Auto is {improvement:.1f}% faster" if improvement > 0 else "Manual is better or equal",
        }