# 🔗 Connecting CHForge to Your Telecom Data Analytics Project

## 📌 Overview

**CHForge** is designed to work with any ClickHouse database. By default, it's pre-configured to connect to the **`telecom_analytics`** database and the **`network_events`** table — which is exactly what your existing project uses.

If you're using the [Telecom Data Analytics](https://github.com/javad-hosseini/telecom_data_analytics) project, **CHForge will work out of the box** with no additional setup.

If you want to use CHForge with a different database or table, you can customize it easily.

---

## 🔗 Default Connection Settings (For Your Telecom Project)

CHForge is configured to connect to:

| Setting | Value |
|---------|-------|
| **Host** | `192.168.247.128` (your ClickHouse server IP) |
| **Port** | `8123` |
| **Database** | `telecom_analytics` |
| **Table** | `network_events` |
| **Username** | `default` |
| **Password** | (empty) |

### Where These Settings Are Defined

| File | What It Does |
|------|--------------|
| `chforge/client/clickhouse_client.py` | Connection logic |
| `test_benchmark.py` / `test_optimizer.py` | Host, port, database values |

---

## ⚙️ Running CHForge on Your Telecom Project

### Option 1: Use Default Settings (Recommended)

If your ClickHouse server is at `192.168.247.128` and your database is `telecom_analytics`, simply run:

```bash
test_optimizer.bat
```

### Option 2: Change Connection Settings

Edit `test_optimizer.py` (or `test_benchmark.py`):

```python
client = ClickHouseClient(
    host="YOUR_CLICKHOUSE_IP",   # ← Change this
    port=8123,                   # ← Change if different
    database="YOUR_DATABASE",    # ← Change to your database
    username="default",          # ← Change if different
    password="",                 # ← Change if needed
)
```

### Option 3: Use Environment Variables (Recommended for Flexibility)

Create a `.env` file in the root of CHForge:

```env
CLICKHOUSE_HOST=192.168.247.128
CLICKHOUSE_PORT=8123
CLICKHOUSE_DATABASE=telecom_analytics
CLICKHOUSE_USERNAME=default
CLICKHOUSE_PASSWORD=
```

Then modify your test files to read from `.env`:

```python
import os
from dotenv import load_dotenv

load_dotenv()

client = ClickHouseClient(
    host=os.getenv("CLICKHOUSE_HOST", "192.168.247.128"),
    port=int(os.getenv("CLICKHOUSE_PORT", 8123)),
    database=os.getenv("CLICKHOUSE_DATABASE", "telecom_analytics"),
    username=os.getenv("CLICKHOUSE_USERNAME", "default"),
    password=os.getenv("CLICKHOUSE_PASSWORD", ""),
)
```

---

## 🏗️ Creating the Database and Table From Scratch

If you haven't set up the telecom database yet, here's how to create it.

### Step 1: Connect to ClickHouse

```bash
clickhouse-client
```

### Step 2: Create the Database

```sql
CREATE DATABASE IF NOT EXISTS telecom_analytics;
```

### Step 3: Create the Network Events Table

```sql
USE telecom_analytics;

CREATE TABLE IF NOT EXISTS network_events (
    event_time DateTime,
    user_id UInt64,
    event_type String,
    country String,
    city String,
    device String,
    network_type String,
    app_name String,
    latency_ms UInt16,
    download_speed Float32,
    packet_loss Float32
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(event_time)
ORDER BY (event_time, user_id)
SETTINGS index_granularity = 8192;
```

### Step 4: Verify Table Creation

```sql
SHOW TABLES;
SELECT count() FROM network_events;
```

### Step 5: Insert Sample Data (Optional)

If you want to test with realistic data, you can use the `generate_data.py` script from your telecom project:

```bash
python generate_data.py
```

Or use the built-in data generator in CHForge (coming soon).

---

## 📊 Table Schema Reference

| Column | Type | Description |
|--------|------|-------------|
| `event_time` | DateTime | Event timestamp |
| `user_id` | UInt64 | User identifier |
| `event_type` | String | DATA_SESSION, CALL_START, etc. |
| `country` | String | Country name |
| `city` | String | City name |
| `device` | String | Device type |
| `network_type` | String | 2G, 3G, 4G, 5G, WiFi |
| `app_name` | String | Application name |
| `latency_ms` | UInt16 | Network latency in milliseconds |
| `download_speed` | Float32 | Download speed in Mbps |
| `packet_loss` | Float32 | Packet loss percentage |

---

## 🔍 Testing Your Connection

Run a simple test to verify everything works:

```bash
# From CHForge directory
test_benchmark.bat
```

Or from Python:

```python
from chforge.client import ClickHouseClient

client = ClickHouseClient(
    host="192.168.247.128",
    port=8123,
    database="telecom_analytics",
)

result = client.query("SELECT count() FROM network_events")
print(f"Total events: {result.result_rows[0][0]}")

client.close()
```

---

## 💡 Tips for Using CHForge with Other Projects

### If You Have a Different Table Structure

1. Edit the SQL queries in `test_benchmark.py` or `test_optimizer.py`
2. Replace `network_events` with your table name
3. Adjust column names to match your schema

### If You Have a Different Database Name

1. Change the `database` parameter in `ClickHouseClient()`
2. Update the SQL queries to use your database

### If You Want to Add CHForge as a Dependency

```bash
pip install -e /path/to/CHForge
```

Then import in your code:

```python
from chforge.benchmark import BenchmarkRunner
from chforge.resources import ResourceConfig
```

---

## 🚀 Quick Start Summary

| Step | Command / Action |
|------|------------------|
| **Clone CHForge** | `git clone https://github.com/javad-hosseini/CHForge.git` |
| **Install deps** | `pip install -r requirements.txt` |
| **Connect to your ClickHouse** | Edit `test_optimizer.py` if needed |
| **Run benchmark** | `test_benchmark.bat` |
| **Run optimizer** | `test_optimizer.bat` |

---

## 📚 Resources

- [Telecom Data Analytics Project](https://github.com/javad-hosseini/telecom_data_analytics)
- [ClickHouse Documentation](https://clickhouse.com/docs)
- [ClickHouse Connect](https://github.com/ClickHouse/clickhouse-connect)

---

**Questions?** Open an issue on the [CHForge GitHub repo](https://github.com/javad-hosseini/CHForge)