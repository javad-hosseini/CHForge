from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class ClickHouseConfig(BaseModel):
    host: str = "localhost"
    port: int = 8123
    database: str = "default"
    username: str = "default"
    password: str = ""


class BenchmarkConfig(BaseModel):
    default_iterations: int = 3
    default_warmup: int = 1
    default_objective: str = "time"
    timeout: int = 300


class ResourceConfigModel(BaseModel):
    threads: Optional[int] = None
    memory: Optional[str] = None
    execution_time: Optional[int] = None
    insert_threads: Optional[int] = None
    block_size: Optional[int] = None


class ProfileModel(BaseModel):
    description: str
    configs: List[ResourceConfigModel]


class QueryModel(BaseModel):
    description: str
    table: str = "network_events"
    sql: str