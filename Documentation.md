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
