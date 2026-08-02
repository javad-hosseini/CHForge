# Phase 1 - Foundation

### **Overview**

Phase 1 of CHForge establishes the foundation for ClickHouse performance benchmarking by implementing **system information collection** and **resource configuration management**.

---

### **What We Built**

#### **1. System Information Collector (`chforge/system/info.py`)**

**Purpose:** Collect detailed hardware and system information from the host machine.

**Features:**
- CPU: Model, physical cores, logical cores (threads), frequency, cache
- GPU: Name, vendor, memory, driver version (NVIDIA, AMD, Intel)
- Memory: Total, used, available, percentage
- Disk: Device, mount point, total/used/free space
- Network: Interface names and IP addresses
- OS: Accurate detection for Windows 10/11, Linux, macOS

**Usage:**
```python
from chforge.system import get_system_info, print_system_info

# Print summary
print_system_info()

# Get as object
info = get_system_info()
print(info.cpu.model)
print(info.memory.total_gb)

# Export as JSON
print(info.to_json())
```

---

#### **2. Resource Configuration (`chforge/resources/config.py`)**

**Purpose:** Define ClickHouse resource settings as a Python dataclass.

**Supported Settings:**

| Attribute | ClickHouse Setting | Description |
|-----------|-------------------|-------------|
| `threads` | `max_threads` | Number of threads for query execution |
| `memory` | `max_memory_usage` | Memory limit (e.g., "8G") |
| `execution_time` | `max_execution_time` | Query timeout in seconds |
| `insert_threads` | `max_insert_threads` | Threads for INSERT operations |
| `block_size` | `max_block_size` | Block size for processing |
| `external_sort` | `max_bytes_before_external_sort` | External sort threshold |
| `external_group_by` | `max_bytes_before_external_group_by` | External group by threshold |
| `join_algorithm` | `join_algorithm` | Join algorithm preference |

**Usage:**
```python
from chforge.resources import ResourceConfig

config = ResourceConfig(
    threads=8,
    memory="8G",
    execution_time=60,
)

# Convert to ClickHouse settings dict
settings = config.to_dict()
# Output: {'max_threads': 8, 'max_memory_usage': '8G', 'max_execution_time': 60}
```

---

#### **3. Resource Manager (`chforge/resources/manager.py`)**

**Purpose:** Generate and manage resource configurations for benchmarking.

**Features:**

**Profile Generation:**
```python
from chforge.resources import ResourceManager

# Generate thread profiles: 2, 4, 8, 16
profiles = ResourceManager.generate_thread_profiles(2, 16, 2)

# Generate memory profiles
profiles = ResourceManager.generate_memory_profiles(['2G', '4G', '8G'])

# Generate all combinations
profiles = ResourceManager.generate_profiles(
    threads=[2, 4, 8],
    memory=['2G', '4G']
)
# Returns: 6 profiles (2x3)
```

**Preset Profiles:**
| Preset | Configurations | Use Case |
|--------|---------------|----------|
| `preset_small()` | 2, 4, 8 threads | Quick testing |
| `preset_medium()` | Threads + memory combinations | Standard benchmarking |
| `preset_full()` | All combinations (2-32 threads, 2-16G memory) | Production benchmarking |
| `preset_quick()` | 4, 8 threads | Very fast test |

**Usage:**
```python
from chforge.resources import ResourceManager

# Use preset
profiles = ResourceManager.preset_medium()

# Merge configs
base = ResourceConfig(threads=4)
override = ResourceConfig(memory="8G")
merged = ResourceManager.merge_settings(base, override)
# Result: threads=4, memory="8G"

# Get default
default = ResourceManager.get_default_config()
```

---

### **Project Structure After Phase 1**

```
CHForge/
├── chforge/
│   ├── __init__.py
│   ├── system/
│   │   ├── __init__.py
│   │   └── info.py              # System info collector
│   ├── resources/
│   │   ├── __init__.py
│   │   ├── config.py            # ResourceConfig dataclass
│   │   └── manager.py           # ResourceManager
│   └── utils/
│       ├── __init__.py
│       └── logger.py
├── test_resources.py            # Test script
├── test_resources.bat           # Batch test runner
├── run_info.bat                 # System info runner
├── requirements.txt
└── README.md
```

---

### **Test Results**

```
✅ System info works (CPU, GPU, Memory, Disk, Network)
✅ ResourceConfig creates valid configurations
✅ ResourceManager generates profiles correctly
✅ Settings conversion to ClickHouse dict works
✅ Presets produce expected configurations
✅ Batch scripts execute successfully
```

---

### **Next Phase: Query Executor**

After Phase 1 completion, the next phase will implement:

1. **ClickHouse Client Integration** - Connect to ClickHouse
2. **Query Executor** - Execute queries with resource configurations
3. **Metrics Collection** - Gather execution metrics (time, memory, rows read)
4. **Benchmark Runner** - Run queries across multiple configurations
5. **Result Analyzer** - Compare and analyze results

---

### **How to Use Phase 1**

```bash
# Get system information
run_info.bat

# Test resource management
test_resources.bat
```

**Or from Python:**
```python
from chforge.system import print_system_info
from chforge.resources import ResourceConfig, ResourceManager

# System info
print_system_info()

# Create config
config = ResourceConfig(threads=8, memory="8G")

# Generate profiles
profiles = ResourceManager.preset_medium()
```

---

### **Phase 1 Summary**

| Component | Status | Description |
|-----------|--------|-------------|
| System Info | ✅ Complete | CPU, GPU, Memory, Disk, Network |
| Resource Config | ✅ Complete | Dataclass with ClickHouse settings |
| Resource Manager | ✅ Complete | Profile generation and presets |
| Settings Builder | ✅ Complete | Config to dict conversion |
| Testing | ✅ Complete | All tests passing |
| Documentation | ✅ Complete | Phase 1 documented |

---

### **Files Added**

```
chforge/system/info.py           ~400 lines
chforge/resources/config.py      ~60 lines
chforge/resources/manager.py     ~150 lines
test_resources.py                ~30 lines
test_resources.bat               ~25 lines
run_info.bat                     ~10 lines
```

---
# Phase 2 - Benchmark Engine

## Overview

Phase 2 of CHForge implements the core benchmarking engine, enabling execution of queries with different resource configurations and collection of performance metrics.

---

### What We Built

#### 1. ClickHouse Client (`chforge/client/clickhouse_client.py`)

**Purpose:** Manage connection to ClickHouse with proper error handling.

**Features:**
- Connection pooling and management
- Query execution with optional settings
- Automatic reconnection on failure
- Connection timeout handling
- Version detection on connection

**Usage:**
```python
from chforge.client import ClickHouseClient

client = ClickHouseClient(
    host="192.168.247.128",
    port=8123,
    database="telecom_analytics",
    username="default",
    password="",
)

# Execute a query
result = client.query("SELECT count() FROM network_events")
print(result.result_rows[0][0])

# Execute with settings
result = client.query(
    "SELECT city, count() FROM network_events GROUP BY city",
    settings={"max_threads": 8}
)

client.close()
```

---

#### 2. Query Executor (`chforge/executor/query_executor.py`)

**Purpose:** Execute queries and collect detailed performance metrics.

**Features:**
- Execute queries with resource configurations
- Collect execution time, rows returned, read bytes, memory usage
- Extract metrics from ClickHouse query summary
- Handle errors gracefully
- Return structured QueryResult objects

**QueryResult Object:**
| Attribute | Description |
|-----------|-------------|
| `execution_time` | Time in seconds to execute the query |
| `rows_returned` | Number of rows in the result set |
| `read_rows` | Number of rows scanned/read from disk |
| `read_bytes` | Amount of data read from disk (bytes) |
| `read_mb` | read_bytes converted to megabytes (property) |
| `memory_usage` | Peak memory usage during query (optional) |
| `error` | Error message if query failed, else None |
| `success` | Boolean indicating if query succeeded |

**Usage:**
```python
from chforge.executor import QueryExecutor
from chforge.resources import ResourceConfig

executor = QueryExecutor(client)

# Execute with default settings
result = executor.execute("SELECT count() FROM network_events")

# Execute with custom resource config
config = ResourceConfig(threads=8, memory="4G")
result = executor.execute(
    "SELECT city, count() FROM network_events GROUP BY city",
    config=config
)

print(f"Time: {result.execution_time:.3f}s")
print(f"Rows: {result.rows_returned}")
print(f"Read: {result.read_mb:.2f} MB")
```

---

#### 3. Benchmark Runner (`chforge/benchmark/runner.py`)

**Purpose:** Run queries across multiple configurations and compare results.

**Features:**
- Execute a query with multiple resource configurations
- Support for warmup runs (discard first N results)
- Support for multiple iterations (average results)
- Generate formatted table output
- Track success/failure counts
- Return structured BenchmarkResult

**BenchmarkResult Object:**
| Attribute | Description |
|-----------|-------------|
| `query` | The SQL query being benchmarked |
| `configs` | List of configurations tested |
| `results` | List of QueryResult objects |
| `total_time` | Total time to run the entire benchmark |
| `iterations_per_config` | Number of iterations per config |
| `success_count` | Number of successful runs |
| `failure_count` | Number of failed runs |

**Usage:**
```python
from chforge.benchmark import BenchmarkRunner
from chforge.resources import ResourceConfig, ResourceManager

runner = BenchmarkRunner(client)

# Define configurations
configs = [
    ResourceConfig(threads=2),
    ResourceConfig(threads=4),
    ResourceConfig(threads=8),
]

# Run benchmark (quick: 1 iteration, no warmup)
result = runner.run_quick(
    sql="SELECT city, count() FROM network_events GROUP BY city",
    configs=configs
)

# Run full benchmark (3 iterations, 1 warmup)
result = runner.run(
    sql="SELECT city, count() FROM network_events GROUP BY city",
    configs=configs,
    iterations=3,
    warmup=1
)

# Print results table
print(result.to_table())
```

---

### Test Results

```
✅ ClickHouse client connects successfully
✅ QueryExecutor executes queries with metrics
✅ BenchmarkRunner runs queries across multiple configs
✅ Results table displays correctly
✅ All 3 configs completed successfully
✅ Connection closes properly
```

### Benchmark Output Example

```
============================================================
BENCHMARK RESULTS
============================================================
+-----------+----------+------------+--------+-----------+----------+
|   Threads | Memory   |   Time (s) |   Rows |   Read MB | Status   |
+===========+==========+============+========+===========+==========+
|         2 | -        |      0.012 |     10 |      0.88 | OK       |
|         4 | -        |      0.012 |     10 |      0.88 | OK       |
|         8 | -        |      0.011 |     10 |      0.88 | OK       |
+-----------+----------+------------+--------+-----------+----------+

Success: 3/3
Failures: 0
Total time: 0.04s
```

---

### Project Structure After Phase 2

```
CHForge/
├── chforge/
│   ├── __init__.py
│   ├── system/
│   │   ├── __init__.py
│   │   └── info.py
│   ├── resources/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── manager.py
│   ├── client/
│   │   ├── __init__.py
│   │   └── clickhouse_client.py      # ← New
│   ├── executor/
│   │   ├── __init__.py
│   │   └── query_executor.py         # ← New
│   ├── benchmark/
│   │   ├── __init__.py
│   │   └── runner.py                 # ← New
│   └── utils/
│       ├── __init__.py
│       └── logger.py
├── test_resources.py
├── test_resources.bat
├── test_benchmark.py                 # ← New
├── test_benchmark.bat                # ← New
├── run_info.bat
├── requirements.txt
└── README.md
```

---

### Phase 2 Summary

| Component | Status | Description |
|-----------|--------|-------------|
| ClickHouse Client | ✅ Complete | Connection management with error handling |
| Query Executor | ✅ Complete | Execute queries and collect metrics |
| Benchmark Runner | ✅ Complete | Run queries across multiple configs |
| Metrics Collection | ✅ Complete | Time, rows, read bytes, memory |
| Result Display | ✅ Complete | Formatted table output |
| Testing | ✅ Complete | All tests passing |

---

### Files Added in Phase 2

```
chforge/client/clickhouse_client.py     ~80 lines
chforge/executor/query_executor.py      ~100 lines
chforge/benchmark/runner.py             ~80 lines
test_benchmark.py                       ~50 lines
test_benchmark.bat                      ~20 lines
```

---

### How to Use Phase 2

```bash
# Run benchmark test
test_benchmark.bat
```

**Or from Python:**
```python
from chforge.client import ClickHouseClient
from chforge.resources import ResourceConfig
from chforge.benchmark import BenchmarkRunner

# Connect
client = ClickHouseClient(
    host="192.168.247.128",
    port=8123,
    database="telecom_analytics",
)

# Define query and configs
sql = "SELECT city, count() FROM network_events GROUP BY city LIMIT 10"
configs = [
    ResourceConfig(threads=2),
    ResourceConfig(threads=4),
    ResourceConfig(threads=8),
]

# Run benchmark
runner = BenchmarkRunner(client)
result = runner.run_quick(sql, configs)

# View results
print(result.to_table())

client.close()
```

---

### Key Learning: Thread Impact

With the benchmark results above, we observed:

- **Small queries (LIMIT 10):** Thread count had minimal impact
- **All configs completed in ~0.012s**
- **Read MB was identical** (~0.88 MB) across all configs
- **No failures** occurred

**Conclusion:** For simple queries, thread configuration doesn't significantly affect performance. Real differences appear with larger datasets and complex aggregations.

---

### Next Phase: Phase 3 - Result Analysis & Reporting

Phase 3 will implement:

1. **Result Analyzer** - Compare and analyze benchmark results
2. **Metrics Visualization** - Generate charts and graphs
3. **Report Generator** - Export results to CSV, JSON, HTML
4. **Best Config Finder** - Automatically identify optimal configuration

---

### Current Status

| Phase | Component | Status |
|-------|-----------|--------|
| Phase 1 | System Info | ✅ Complete |
| Phase 1 | Resource Manager | ✅ Complete |
| Phase 2 | ClickHouse Client | ✅ Complete |
| Phase 2 | Query Executor | ✅ Complete |
| Phase 2 | Benchmark Runner | ✅ Complete |
| Phase 3 | Result Analyzer | ⏳ Pending |
| Phase 3 | Report Generator | ⏳ Pending |
| Phase 4 | Visualization | ⏳ Pending |

---

**Phase 2 Status: COMPLETE ✅**

Ready for Phase 3: Result Analysis & Reporting 🚀