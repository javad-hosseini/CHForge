# 📖 CHForge CLI Guide

## 🎯 **What is `run.py`?**

`run.py` is the main entry point for CHForge. With this tool you can:
- **Run benchmarks** - Test a query with multiple configurations
- **Optimize** - Find the best configuration for a query automatically
- **List queries and profiles** - Discover available resources

---

## 🚀 **Command Structure:**

```bash
python run.py [OPTIONS]
```

---

## 📋 **1. Listing Queries and Profiles:**

### **List available queries:**
```bash
python run.py --list-queries
```

**Output:**
```
📋 Available Queries:
----------------------------------------
  heavy_agg: Heavy aggregation on city, network, app
  light_agg: Simple city aggregation
  full_scan: Full table scan with filters
  time_series: Daily time series aggregation
----------------------------------------
```

### **List available profiles:**
```bash
python run.py --list-profiles
```

**Output:**
```
📋 Available Profiles:
----------------------------------------
  quick: Quick test with 2 configs
  standard: Standard benchmark with thread scaling
  memory_test: Test memory configurations
  full: Full benchmark (threads + memory combinations)
----------------------------------------
```

---

## 📊 **2. Running Benchmarks:**

### **Quick benchmark:**
```bash
python run.py --query light_agg --profile quick
```

### **With advanced settings:**
```bash
python run.py --query heavy_agg --profile standard --iterations 5 --warmup 2
```

### **Override database connection:**
```bash
python run.py --query heavy_agg --host 192.168.1.100 --database my_db
```

**Sample Output:**
```
============================================================
📊 CHForge Benchmark
============================================================
📌 Query: heavy_agg - Heavy aggregation on city, network, app
📋 Profile: standard - Standard benchmark with thread scaling
⚙️  Configs: 4
🔄 Iterations: 5, Warmup: 2
============================================================

📊 BENCHMARK RESULTS:
============================================================
+-----------+----------+------------+--------+-----------+----------+
|   Threads | Memory   |   Time (s) |   Rows |   Read MB | Status   |
+===========+==========+============+========+===========+==========+
|         2 | -        |      0.045 |     50 |     12.34 | OK       |
|         4 | -        |      0.038 |     50 |     12.34 | OK       |
|         8 | -        |      0.035 |     50 |     12.34 | OK       |
|        16 | -        |      0.034 |     50 |     12.34 | OK       |
+-----------+----------+------------+--------+-----------+----------+

✅ Success: 20/20
❌ Failures: 0
⏱️  Total time: 1.52s
```

---

## 🧠 **3. Running the Optimizer:**

### **Optimize for time:**
```bash
python run.py --optimize --query heavy_agg --objective time
```

### **Optimize for memory:**
```bash
python run.py --optimize --query heavy_agg --objective memory
```

**Sample Output:**
```
============================================================
📊 CHForge Benchmark
============================================================
📌 Query: heavy_agg - Heavy aggregation on city, network, app
📋 Profile: standard (4 configs)
🔄 Iterations: 3, Warmup: 1
============================================================

🏆 OPTIMIZATION RESULT:
============================================================
Best config: ResourceConfig(threads=4, memory=4G)
Best time: 0.0380s
Configs tested: 10
Success rate: 100%

Recommendation:
Objective: Minimize time
Best config: ResourceConfig(threads=4, memory=4G)
Best time: 0.0380s
Improvement: 28.9% faster than worst config
Success rate: 10/10
Tip: Your query may be I/O or memory bound.
```

---

## 📋 **4. System Information Commands:**

### **Local system info:**
```bash
python run.py --system-info
```

### **ClickHouse server info:**
```bash
python run.py --clickhouse-info
```

**Sample Output (clickhouse-info):**
```
======================================================================
📊 CLICKHOUSE SERVER INFORMATION
======================================================================

📌 Version: 26.4.5.143
📌 Uptime: 0d 1h 23m

----------------------------------------------------------------------
💻 CPU:
   Total Cores: 8
   CPU Usage: 5.0%
   Load Average (1m): 0.30

----------------------------------------------------------------------
🧠 Memory:
   Total: 8.00 GB
   Used: 0.78 GB (9.7%)
   Free: 7.22 GB

----------------------------------------------------------------------
💾 Disk:
   Total: 39.20 GB
   Used: 29.26 GB (74.6%)
   Free: 9.94 GB

======================================================================
```

---

## ⚙️ **5. Default Configuration (`config.yaml`):**

```yaml
clickhouse:
  host: "192.168.247.128"      # Server IP
  port: 8123                   # Port
  database: "telecom_analytics" # Database name
  username: "default"          # Username
  password: ""                 # Password

benchmark:
  default_iterations: 3        # Number of iterations
  default_warmup: 1            # Number of warmup runs
  default_objective: "time"    # Default objective (time/memory)
  timeout: 300                 # Max execution time per query (seconds)
```

---

## 📝 **6. Adding a New Query:**

Add to `configs/queries.yaml`:

```yaml
queries:
  my_new_query:
    description: "My custom query"
    table: "network_events"
    sql: |
      SELECT city, count() as total
      FROM {table}
      WHERE event_time > now() - INTERVAL 7 DAY
      GROUP BY city
      ORDER BY total DESC
```

Then run:
```bash
python run.py --query my_new_query --profile standard
```

---

## 📊 **7. Adding a New Profile:**

Add to `configs/profiles.yaml`:

```yaml
profiles:
  my_profile:
    description: "My custom profile"
    configs:
      - threads: 2
        memory: "2G"
      - threads: 4
        memory: "4G"
      - threads: 8
        memory: "8G"
```

Then run:
```bash
python run.py --query heavy_agg --profile my_profile
```

---

## 🎯 **8. Command Line Options Summary:**

| Option | Description | Example |
|--------|-------------|---------|
| `--query, -q` | Query name from `queries.yaml` | `--query heavy_agg` |
| `--profile, -p` | Profile name from `profiles.yaml` | `--profile standard` |
| `--iterations, -i` | Number of iterations | `--iterations 5` |
| `--warmup, -w` | Number of warmup runs | `--warmup 2` |
| `--optimize, -o` | Run optimizer | `--optimize` |
| `--objective` | Optimization objective (time/memory) | `--objective memory` |
| `--host` | Override ClickHouse host | `--host 192.168.1.100` |
| `--database` | Override database name | `--database my_db` |
| `--list-queries` | List all queries | `--list-queries` |
| `--list-profiles` | List all profiles | `--list-profiles` |
| `--system-info` | Show local system info | `--system-info` |
| `--clickhouse-info` | Show ClickHouse server info | `--clickhouse-info` |

---

## 💡 **9. Important Notes:**

| Profile | Description | Use Case |
|---------|-------------|----------|
| **Quick** | 2 configs (4, 8 threads) | Fast testing |
| **Standard** | 4 configs (2, 4, 8, 16 threads) | Regular benchmarking |
| **Memory_Test** | 3 configs with different memory | Memory testing |
| **Full** | Thread + memory combinations | Comprehensive testing |
| **Warmup** | Initial runs discarded (cache warmup) | Reducing cache bias |
| **Iterations** | Number of executions per config (averaged) | Statistical confidence |

---

## 🚀 **10. Common Scenarios:**

### **Scenario 1: Quick query test**
```bash
python run.py --query light_agg --profile quick
```

### **Scenario 2: Full benchmark on heavy query**
```bash
python run.py --query heavy_agg --profile standard --iterations 5 --warmup 2
```

### **Scenario 3: Find best configuration**
```bash
python run.py --optimize --query heavy_agg --objective time
```

### **Scenario 4: Test on a different database**
```bash
python run.py --query heavy_agg --host 192.168.1.50 --database sales_db
```

### **Scenario 5: Custom query with custom profile**
```bash
python run.py --query my_new_query --profile my_profile
```

### **Scenario 6: Check system information**
```bash
python run.py --system-info
python run.py --clickhouse-info
```

---

**Happy Benchmarking! 🚀**