# 🧠 AI + Data Engineer Challenge – 8 Figure Agency (ENGLISH)

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

## 🚀 Local Deployment (Make)

```bash
make run           # Launches API on localhost:8500
make test-ingest   # Bulk inserts test records
```

SQLite database is stored at `data/ads.db`.

---

## 🔄 Data Ingestion with n8n

1. Open your n8n instance (`http://localhost:5678`)
2. Import `ads_ingest_metrics_workflow_FIXED.json`
3. Update `POST /ingest` node URL to `http://localhost:8500/ingest`
4. Enable the workflow (cron: every 60 minutes)
5. Run manually or let it schedule

---

## 📊 KPIs exposed at /metrics

Endpoint:

```
GET http://localhost:8500/metrics?start=YYYY-MM-DD&end=YYYY-MM-DD
```

Returns:

```json
{
  "start": "2024-07-01",
  "end": "2024-08-01",
  "current_period": {
    "spend": 190,
    "conversions": 17,
    "CAC": 11.18,
    "ROAS": 8.95
  },
  "previous_period": { ... },
  "delta_pct": {
    "CAC_change_pct": 12.3,
    "ROAS_change_pct": -4.5
  }
}
```

Assumes: `revenue = conversions * 100`

---

## 📹 Loom Demo (optional)

Record a short demo explaining:

- How data is ingested via n8n
- How CAC and ROAS are computed
- How to use the `/metrics` endpoint
- Key decisions made

---

## 📎 Challenge Reference

- CSV file: ads_spend.csv (Google Drive)
- Deliverables: n8n workflow, working API, KPIs in SQL, README and demo

---

## 🧪 SQL Examples (KPIs)

```sql
-- CAC: Customer Acquisition Cost
SELECT SUM(spend)/NULLIF(SUM(conversions),0) AS CAC FROM ads_spend;

-- ROAS: Return On Ad Spend
SELECT (SUM(conversions)*100.0)/NULLIF(SUM(spend),0) AS ROAS FROM ads_spend;
```

---

## 👤 Author

Eliab Lemus Barrios  
Guatemala 🇬🇹  
DevOps | Data Engineer | SRE
# 🧠 AI + Data Engineer Challenge – 8 Figure Agency

Este repositorio contiene la solución completa al reto técnico para el rol de *AI Data Engineer*. La implementación es minimalista, reproducible y cumple con los requerimientos usando solo herramientas open-source.

---

## ⚙️ Tecnologías usadas

- **FastAPI** + **SQLite** para la API de ingestión y KPIs
- **n8n Community Edition** para orquestación de ingestion + acceso a métricas
- **Docker** y `Makefile` para despliegue y testing local

---

## 📦 Estructura del repositorio

```
.
├── main.py                      # API FastAPI con endpoints /ingest y /metrics
├── Dockerfile
├── Makefile
├── test_payload.json            # Ejemplo de inserción bulk
├── ads_ingest_metrics_workflow_FIXED.json  # Workflow de n8n
├── requirements.txt
└── README.md
```

---

## 🚀 Despliegue local (usando Make)

```bash
make run        # Lanza la app en localhost:8500
make test-ingest  # Inserta datos de prueba (bulk)
```

La base SQLite se guarda en `data/ads.db`.

---

## 🔄 Ingesta de datos con n8n

1. Ingrese a su instancia de n8n (`http://localhost:5678`)
2. Importar → `ads_ingest_metrics_workflow_FIXED.json`
3. Reemplace la URL del nodo `POST /ingest` por `http://localhost:8500/ingest`
4. Habilite el workflow (cron cada 60 min)
5. Puede ejecutar manualmente o dejarlo en automático

---

## 📊 KPIs expuestos (API /metrics)

Endpoint disponible:

```
GET http://localhost:8500/metrics?start=YYYY-MM-DD&end=YYYY-MM-DD
```

Responde:

```json
{
  "start": "2024-07-01",
  "end": "2024-08-01",
  "current_period": {
    "spend": 190,
    "conversions": 17,
    "CAC": 11.18,
    "ROAS": 8.95
  },
  "previous_period": { ... },
  "delta_pct": {
    "CAC_change_pct": 12.3,
    "ROAS_change_pct": -4.5
  }
}
```

Este cálculo asume: `revenue = conversions * 100`

---

## 📹 Loom Demo (opcional)

Puede grabar una demo rápida explicando:

- Cómo se ingestan los datos vía n8n
- Cómo se calcula CAC y ROAS
- Cómo consultar el endpoint `/metrics`
- Qué decisiones tomó y por qué

---

## 📎 Referencias del reto

- Archivo CSV: ads_spend.csv (desde Google Drive)
- Entregables: n8n workflow, API funcional, SQL KPIs, README y demo

---

## 🧪 SQL de ejemplo (KPIs)

```sql
-- CAC: Costo por Adquisición
SELECT SUM(spend)/NULLIF(SUM(conversions),0) AS CAC FROM ads_spend;

-- ROAS: Retorno sobre Ad Spend
SELECT (SUM(conversions)*100.0)/NULLIF(SUM(spend),0) AS ROAS FROM ads_spend;
```

---

## 👤 Autor

Eliab Lemus Barrios  
Guatemala 🇬🇹  
DevOps | Data Engineer | SRE  

---
