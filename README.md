# 🧠 AI + Data Engineer Challenge – 8 Figure Agency

This repository contains the complete solution to the technical challenge for the *AI Data Engineer* role. The implementation is minimalist, reproducible, and uses only open-source tools.

---

## ⚙️ Tech Stack

- **FastAPI** + **SQLite** for the ingestion API and KPIs
- **n8n Community Edition** for ingestion orchestration + metrics access
- **Docker** and `Makefile` for local deployment and testing

---

## 📦 Repository Structure

```
.
├── main.py                      # FastAPI with /ingest and /metrics endpoints
├── Dockerfile
├── Makefile
├── test_payload.json            # Sample bulk insert payload
├── ads_ingest_metrics_workflow_FIXED.json  # n8n workflow
├── requirements.txt
└── README.md
```

---

## 🚀 Local Deployment

```bash
make run           # Launches API on localhost:8500
make test-ingest   # Bulk inserts test records
```

SQLite database is stored in `data/ads.db`.

---

## 🔄 Data Ingestion with n8n

1. Open your n8n instance (`http://localhost:5678`)
2. Import `ads_ingest_metrics_workflow_FIXED.json`
3. Update `POST /ingest` node URL to `http://localhost:8500/ingest`
4. Enable the workflow (cron: every 60 minutes)
5. Run manually or let it schedule

---

## 📊 KPIs exposed at `/metrics`

### Option 1 – Direct date range:

```bash
GET /metrics?start=2025-03-01&end=2025-04-01
```

Returns:

```json
{
  "spend": 269988.28,
  "conversions": 8908,
  "cac": 30.31,
  "roas": 3.30
}
```

### Option 2 – Last 30 days vs Previous 30 days

```bash
GET /metrics?compare=last30_prev30
```

Returns:

```json
{
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
```

This comparison logic is implemented directly in the API.

---

## 📎 Challenge Reference

- CSV file: ads_spend.csv (from Google Drive)
- Deliverables: n8n workflow, working API, SQL KPIs, README and optional Loom demo

---

## 📐 KPI Formulas

```sql
-- CAC: Customer Acquisition Cost
SELECT SUM(spend)/NULLIF(SUM(conversions),0) AS CAC FROM ads_spend;

-- ROAS: Return On Ad Spend
SELECT (SUM(conversions)*100.0)/NULLIF(SUM(spend),0) AS ROAS FROM ads_spend;
```

Assumes: `revenue = conversions × 100`

---

## 📹 Loom Demo (optional)

Record a 2–4 minute video explaining:

- How data is ingested via n8n
- How CAC and ROAS are calculated
- How to use the `/metrics` endpoint
- Key implementation decisions

---

## 👤 Author

Eliab Lemus Barrios  
Guatemala 🇬🇹  
DevOps | Data Engineer | SRE