
# 📖 CHForge CLI Guide

## 🎯 **`run.py` چیه؟**

`run.py` ورودی اصلی CHForge هست. با این ابزار می‌تونی:
- **بنچمارک** اجرا کنی (یک کوئری رو با چندین کانفیگ مختلف تست کنی)
- **اپتیمایز** کنی (بهترین کانفیگ رو برای یک کوئری پیدا کنی)
- **کوئری‌ها و پروفایل‌ها** رو لیست کنی

---

## 🚀 **ساختار کلی دستورات:**

```bash
python run.py [OPTIONS]
```

---

## 📋 **۱. لیست کردن کوئری‌ها و پروفایل‌ها:**

### **لیست کوئری‌های موجود:**
```bash
python run.py --list-queries
```

**خروجی:**
```
📋 Available Queries:
----------------------------------------
  heavy_agg: Heavy aggregation on city, network, app
  light_agg: Simple city aggregation
  full_scan: Full table scan with filters
  time_series: Daily time series aggregation
----------------------------------------
```

### **لیست پروفایل‌های موجود:**
```bash
python run.py --list-profiles
```

**خروجی:**
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

## 📊 **۲. اجرای بنچمارک:**

### **ساده‌ترین حالت:**
```bash
python run.py --query light_agg --profile quick
```

### **با تنظیمات کامل‌تر:**
```bash
python run.py --query heavy_agg --profile standard --iterations 5 --warmup 2
```

### **با override اتصال به دیتابیس:**
```bash
python run.py --query heavy_agg --host 192.168.1.100 --database my_db
```

**خروجی نمونه:**
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

## 🧠 **۳. اجرای اپتیمایزر:**

### **اپتیمایز برای زمان (time):**
```bash
python run.py --optimize --query heavy_agg --objective time
```

### **اپتیمایز برای حافظه (memory):**
```bash
python run.py --optimize --query heavy_agg --objective memory
```

**خروجی نمونه:**
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

## ⚙️ **۴. تنظیمات پیش‌فرض در `config.yaml`:**

```yaml
clickhouse:
  host: "192.168.247.128"      # آی‌پی سرور
  port: 8123                   # پورت
  database: "telecom_analytics" # دیتابیس
  username: "default"          # کاربر
  password: ""                 # رمز

benchmark:
  default_iterations: 3        # تعداد دفعات اجرا
  default_warmup: 1            # تعداد دفعات گرم کردن
  default_objective: "time"    # هدف پیش‌فرض (time/memory)
  timeout: 300                 # حداکثر زمان هر اجرا (ثانیه)
```

---

## 📝 **۵. اضافه کردن کوئری جدید:**

به `configs/queries.yaml` اضافه کن:

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

بعد اجرا کن:
```bash
python run.py --query my_new_query --profile standard
```

---

## 📊 **۶. اضافه کردن پروفایل جدید:**

به `configs/profiles.yaml` اضافه کن:

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

بعد اجرا کن:
```bash
python run.py --query heavy_agg --profile my_profile
```

---

## 🎯 **۷. جمع‌بندی گزینه‌های خط فرمان:**

| گزینه | توضیح | مثال |
|-------|-------|------|
| `--query, -q` | نام کوئری از `queries.yaml` | `--query heavy_agg` |
| `--profile, -p` | نام پروفایل از `profiles.yaml` | `--profile standard` |
| `--iterations, -i` | تعداد دفعات اجرا | `--iterations 5` |
| `--warmup, -w` | تعداد دفعات گرم کردن | `--warmup 2` |
| `--optimize, -o` | اجرای اپتیمایزر | `--optimize` |
| `--objective` | هدف بهینه‌سازی (time/memory) | `--objective memory` |
| `--host` | override آی‌پی سرور | `--host 192.168.1.100` |
| `--database` | override نام دیتابیس | `--database my_db` |
| `--list-queries` | لیست کوئری‌ها | `--list-queries` |
| `--list-profiles` | لیست پروفایل‌ها | `--list-profiles` |

---

## 💡 **۸. نکات مهم:**

| نکته | توضیح |
|-------|-------|
| **پروفایل Quick** | ۲ تا کانفیگ (۴ و ۸ ترد) - برای تست سریع |
| **پروفایل Standard** | ۴ تا کانفیگ (۲، ۴، ۸، ۱۶ ترد) - برای بنچمارک معمولی |
| **پروفایل Memory_Test** | ۳ تا کانفیگ با حافظه‌های مختلف - برای تست حافظه |
| **پروفایل Full** | ترکیب ترد و حافظه - برای تست کامل |
| **Warmup** | دفعات اجرای اولیه که نتایجش دور ریخته میشه (برای گرم کردن کش) |
| **Iterations** | تعداد دفعات اجرا برای هر کانفیگ (میانگین گرفته میشه) |

---

## 🚀 **۹. سناریوهای معمول:**

### **سناریو ۱: تست سریع یک کوئری**
```bash
python run.py --query light_agg --profile quick
```

### **سناریو ۲: بنچمارک کامل روی کوئری سنگین**
```bash
python run.py --query heavy_agg --profile standard --iterations 5 --warmup 2
```

### **سناریو ۳: پیدا کردن بهترین تنظیمات**
```bash
python run.py --optimize --query heavy_agg --objective time
```

### **سناریو ۴: تست روی دیتابیس دیگه**
```bash
python run.py --query heavy_agg --host 192.168.1.50 --database sales_db
```

### **سناریو ۵: تست کوئری جدید با پروفایل سفارشی**
```bash
python run.py --query my_new_query --profile my_profile
```
