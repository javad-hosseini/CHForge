from pathlib import Path
from typing import Dict, Any, Optional, List

import yaml

from .models import ClickHouseConfig, BenchmarkConfig


class ConfigLoader:
    """Load configuration from YAML files"""

    def __init__(self, config_dir: str = "configs"):
        self.config_dir = Path(config_dir)
        self._config: Optional[Dict] = None
        self._queries: Optional[Dict] = None
        self._profiles: Optional[Dict] = None

    def load_config(self) -> Dict[str, Any]:
        """Load config.yaml"""
        if self._config is None:
            with open(self.config_dir / "config.yaml", encoding="utf-8") as f:
                self._config = yaml.safe_load(f)
        return self._config

    def load_queries(self) -> Dict[str, Any]:
        """Load queries.yaml"""
        if self._queries is None:
            with open(self.config_dir / "queries.yaml", encoding="utf-8") as f:
                self._queries = yaml.safe_load(f)
        return self._queries

    def load_profiles(self) -> Dict[str, Any]:
        """Load profiles.yaml"""
        if self._profiles is None:
            with open(self.config_dir / "profiles.yaml", encoding="utf-8") as f:
                self._profiles = yaml.safe_load(f)
        return self._profiles

    def list_queries(self) -> List[str]:
        """List all available query names"""
        queries = self.load_queries()
        return list(queries.get("queries", {}).keys())

    def list_profiles(self) -> List[str]:
        """List all available profile names"""
        profiles = self.load_profiles()
        return list(profiles.get("profiles", {}).keys())

    def get_query_description(self, name: str) -> str:
        """Get query description"""
        queries = self.load_queries()
        query_data = queries["queries"].get(name)
        if not query_data:
            return ""
        return query_data.get("description", "")

    def get_profile_description(self, name: str) -> str:
        """Get profile description"""
        profiles = self.load_profiles()
        profile_data = profiles["profiles"].get(name)
        if not profile_data:
            return ""
        return profile_data.get("description", "")

    def get_query(self, name: str) -> str:
        """Get a query by name with table substitution"""
        queries = self.load_queries()
        query_data = queries["queries"].get(name)
        if not query_data:
            available = list(queries["queries"].keys())
            raise ValueError(f"Query '{name}' not found. Available: {available}")

        sql = query_data["sql"]
        table = query_data.get("table", "network_events")
        return sql.format(table=table)

    def get_profile(self, name: str) -> List[Dict[str, Any]]:
        """Get a profile by name"""
        profiles = self.load_profiles()
        profile_data = profiles["profiles"].get(name)
        if not profile_data:
            available = list(profiles["profiles"].keys())
            raise ValueError(f"Profile '{name}' not found. Available: {available}")

        return profile_data["configs"]

    def get_clickhouse_config(self) -> Dict[str, Any]:
        """Get ClickHouse connection settings"""
        config = self.load_config()
        return config.get("clickhouse", {})

    def get_clickhouse_config_model(self) -> ClickHouseConfig:
        """Get ClickHouse connection settings as Pydantic model"""
        return ClickHouseConfig(**self.get_clickhouse_config())

    def get_benchmark_config(self) -> Dict[str, Any]:
        """Get benchmark default settings"""
        config = self.load_config()
        return config.get("benchmark", {})

    def get_benchmark_config_model(self) -> BenchmarkConfig:
        """Get benchmark default settings as Pydantic model"""
        return BenchmarkConfig(**self.get_benchmark_config())
