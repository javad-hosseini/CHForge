from typing import List, Dict, Any, Optional
from .config import ResourceConfig


class ResourceManager:
    """
    Manages resource configurations for ClickHouse queries
    """

    @staticmethod
    def build_settings(config: ResourceConfig) -> Dict[str, Any]:
        """Convert ResourceConfig to ClickHouse settings dict"""
        return config.to_dict()

    @staticmethod
    def merge_settings(base: ResourceConfig, override: ResourceConfig) -> ResourceConfig:
        """Merge two configs, override takes priority"""
        merged = ResourceConfig()

        for field in ["threads", "memory", "execution_time", "insert_threads",
                      "block_size", "external_sort", "external_group_by", "join_algorithm"]:
            base_val = getattr(base, field)
            override_val = getattr(override, field)
            setattr(merged, field, override_val if override_val is not None else base_val)

        merged.extra = {**base.extra, **override.extra}
        return merged

    # ============================================
    # GENERATE PROFILES FOR BENCHMARK
    # ============================================

    @staticmethod
    def generate_thread_profiles(
            min_threads: int = 2,
            max_threads: int = 16,
            step: int = 2
    ) -> List[ResourceConfig]:
        """Generate thread profiles: 2,4,8,16,..."""
        profiles = []
        for t in range(min_threads, max_threads + 1, step):
            profiles.append(ResourceConfig(threads=t))
        return profiles

    @staticmethod
    def generate_memory_profiles(memory_values: List[str]) -> List[ResourceConfig]:
        """Generate memory profiles: ['2G','4G','8G']"""
        return [ResourceConfig(memory=mem) for mem in memory_values]

    @staticmethod
    def generate_combined_profiles(
            threads: List[int],
            memory: List[str],
    ) -> List[ResourceConfig]:
        """Generate all combinations of threads and memory"""
        profiles = []
        for t in threads:
            for m in memory:
                profiles.append(ResourceConfig(threads=t, memory=m))
        return profiles

    @staticmethod
    def generate_profiles(
            threads: Optional[List[int]] = None,
            memory: Optional[List[str]] = None,
            execution_time: Optional[List[int]] = None,
            block_size: Optional[List[int]] = None,
    ) -> List[ResourceConfig]:
        """
        Generate all combinations of given parameters

        Example:
            profiles = ResourceManager.generate_profiles(
                threads=[2, 4, 8],
                memory=['2G', '4G'],
                execution_time=[60, 300]
            )
            # Returns: 2x2x2 = 8 profiles
        """
        import itertools

        params = []
        param_names = []

        if threads:
            params.append(threads)
            param_names.append('threads')
        if memory:
            params.append(memory)
            param_names.append('memory')
        if execution_time:
            params.append(execution_time)
            param_names.append('execution_time')
        if block_size:
            params.append(block_size)
            param_names.append('block_size')

        profiles = []
        for combination in itertools.product(*params):
            kwargs = dict(zip(param_names, combination))
            profiles.append(ResourceConfig(**kwargs))

        return profiles

    # ============================================
    # PRESET PROFILES
    # ============================================

    @staticmethod
    def preset_small() -> List[ResourceConfig]:
        """Small benchmark profiles (for testing)"""
        return [
            ResourceConfig(threads=2),
            ResourceConfig(threads=4),
            ResourceConfig(threads=8),
        ]

    @staticmethod
    def preset_medium() -> List[ResourceConfig]:
        """Medium benchmark profiles"""
        return [
            ResourceConfig(threads=2, memory="2G"),
            ResourceConfig(threads=4, memory="4G"),
            ResourceConfig(threads=8, memory="8G"),
            ResourceConfig(threads=16, memory="8G"),
        ]

    @staticmethod
    def preset_full() -> List[ResourceConfig]:
        """Full benchmark profiles (for production)"""
        return ResourceManager.generate_combined_profiles(
            threads=[2, 4, 8, 16, 32],
            memory=["2G", "4G", "8G", "16G"],
        )

    @staticmethod
    def preset_quick() -> List[ResourceConfig]:
        """Quick benchmark (just to test)"""
        return [
            ResourceConfig(threads=4),
            ResourceConfig(threads=8),
        ]

    @staticmethod
    def get_default_config() -> ResourceConfig:
        """Get default ClickHouse settings"""
        return ResourceConfig(
            threads=4,
            memory="4G",
            execution_time=300,
        )