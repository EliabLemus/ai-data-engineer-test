# 📘 API Reference – FastAPI Metrics API

This API provides endpoints to ingest advertising data and compute key marketing KPIs such as CAC and ROAS.

---

## 🛠️ `POST /ingest`

Inserts one or more campaign records into the `ads_spend` table.

### 🔹 Input format:
- Accepts a **single object** or a **list of objects**
- Required fields: `date`, `platform`, `account`, `campaign`, `country`, `device`, `spend`, `clicks`, `impressions`, `conversions`, `load_date`, `source_file_name`

### 🧠 Optimizations:
- Uses `executemany()` for batch inserts
- SQLite `PRAGMA` settings for write performance

### ✅ Example payload:

```json
[
  {
    "date": "2025-03-30",
    "platform": "Meta",
    "account": "AcctA",
    "campaign": "Prospecting",
    "country": "MX",
    "device": "Mobile",
    "spend": 100.0,
    "clicks": 200,
    "impressions": 5000,
    "conversions": 10,
    "load_date": "2025-08-28",
    "source_file_name": "ads_spend.csv"
  }
]
```

---

## 📊 `GET /metrics`

This endpoint calculates CAC and ROAS based on filters.

### 🧩 Option 1: Custom range query

```http
GET /metrics?start=2025-03-01&end=2025-04-01
```

Returns:

```json
{
  "status": "ok",
  "range": {
    "start": "2025-03-01",
    "end": "2025-04-01"
  },
  "spend": 4500.0,
  "conversions": 150,
  "cac": 30.0,
  "roas": 3.33
}
```

---

### 🧩 Option 2: Auto compare last 30 vs previous 30 days

```http
GET /metrics?compare=last30_prev30
```

Returns:

```json
{
  "status": "ok",
  "result": {
    "last_30d": {
      "spend": 269988.28,
      "conversions": 8908,
      "cac": 30.31,
      "roas": 3.30
    },
    "prev_30d": {
      "spend": 240000.00,
      "conversions": 7500,
      "cac": 32.00,
      "roas": 3.12
    },
    "delta_pct": {
      "spend": 0.12,
      "conversions": 0.18,
      "cac": -0.052,
      "roas": 0.058
    }
  }
}
```

This output satisfies:

- Comparison between last and previous period  
- Absolute values + percent change (deltas)  
- Ready for table rendering  

---

## 📐 KPI Definitions

| KPI  | Formula |
|------|---------|
| **CAC**  | `CAC = spend / conversions` |
| **ROAS** | `ROAS = (conversions × 100) / spend` |
| **Δ %**  | `delta = (current - previous) / previous` |

> Assumes revenue = conversions × 100

---

## ✅ `GET /health`

Simple healthcheck endpoint to verify the server is running:

```bash
curl https://your-host/health
```

Returns:

```json
{ "status": "ok" }
```