import yaml
from pathlib import Path
from typing import Dict, Any, Optional


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
            with open(self.config_dir / "config.yaml") as f:
                self._config = yaml.safe_load(f)
        return self._config

    def load_queries(self) -> Dict[str, Any]:
        """Load queries.yaml"""
        if self._queries is None:
            with open(self.config_dir / "queries.yaml") as f:
                self._queries = yaml.safe_load(f)
        return self._queries

    def load_profiles(self) -> Dict[str, Any]:
        """Load profiles.yaml"""
        if self._profiles is None:
            with open(self.config_dir / "profiles.yaml") as f:
                self._profiles = yaml.safe_load(f)
        return self._profiles

    def get_query(self, name: str) -> str:
        """Get a query by name with table substitution"""
        queries = self.load_queries()
        query_data = queries["queries"].get(name)
        if not query_data:
            raise ValueError(f"Query '{name}' not found")

        sql = query_data["sql"]
        table = query_data.get("table", "network_events")
        return sql.format(table=table)

    def get_profile(self, name: str) -> list:
        """Get a profile by name"""
        profiles = self.load_profiles()
        profile_data = profiles["profiles"].get(name)
        if not profile_data:
            raise ValueError(f"Profile '{name}' not found")

        return profile_data["configs"]

    def get_clickhouse_config(self) -> Dict[str, Any]:
        """Get ClickHouse connection settings"""
        config = self.load_config()
        return config.get("clickhouse", {})

    def get_benchmark_config(self) -> Dict[str, Any]:
        """Get benchmark default settings"""
        config = self.load_config()
        return config.get("benchmark", {})