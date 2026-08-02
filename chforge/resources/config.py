from dataclasses import dataclass, field
from typing import Optional, Dict, Any


@dataclass
class ResourceConfig:
    """
    Resource configuration for ClickHouse queries
    """

    threads: Optional[int] = None
    memory: Optional[str] = None
    execution_time: Optional[int] = None
    insert_threads: Optional[int] = None
    block_size: Optional[int] = None
    external_sort: Optional[str] = None
    external_group_by: Optional[str] = None
    join_algorithm: Optional[str] = None

    extra: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to ClickHouse settings dictionary"""
        settings = {}

        if self.threads is not None:
            settings["max_threads"] = self.threads
        if self.memory is not None:
            settings["max_memory_usage"] = self.memory
        if self.execution_time is not None:
            settings["max_execution_time"] = self.execution_time
        if self.insert_threads is not None:
            settings["max_insert_threads"] = self.insert_threads
        if self.block_size is not None:
            settings["max_block_size"] = self.block_size
        if self.external_sort is not None:
            settings["max_bytes_before_external_sort"] = self.external_sort
        if self.external_group_by is not None:
            settings["max_bytes_before_external_group_by"] = self.external_group_by
        if self.join_algorithm is not None:
            settings["join_algorithm"] = self.join_algorithm

        settings.update(self.extra)
        return settings

    def __repr__(self) -> str:
        parts = []
        if self.threads:
            parts.append(f"threads={self.threads}")
        if self.memory:
            parts.append(f"memory={self.memory}")
        if self.execution_time:
            parts.append(f"exec_time={self.execution_time}s")
        return f"ResourceConfig({', '.join(parts)})"