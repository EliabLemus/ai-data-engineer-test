from fastapi import FastAPI, Body, Query
from typing import Any, Dict, List, Optional, Tuple
import os, sqlite3
from contextlib import contextmanager
from datetime import datetime

DB_PATH = os.environ.get("SQLITE_DB_PATH", "/app/sqliteapi/data/ADS_METRICS.sqlite")

def init_db() -> str:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    con = sqlite3.connect(DB_PATH)
    con.executescript("""
    PRAGMA journal_mode = WAL;
    PRAGMA synchronous = NORMAL;
    CREATE TABLE IF NOT EXISTS ads_spend (
      date TEXT,
      platform TEXT,
      account TEXT,
      campaign TEXT,
      country TEXT,
      device TEXT,
      spend REAL,
      clicks INTEGER,
      impressions INTEGER,
      conversions INTEGER,
      load_date TEXT,
      source_file_name TEXT
    );
    CREATE INDEX IF NOT EXISTS idx_ads_date ON ads_spend(date);
    """)
    con.commit()
    con.close()
    return DB_PATH

@contextmanager
def get_conn(row_factory=None):
    con = sqlite3.connect(DB_PATH, check_same_thread=False)
    if row_factory:
        con.row_factory = row_factory
    try:
        yield con
    finally:
        con.close()

def dict_factory(cursor, row):
    return {col[0]: row[i] for i, col in enumerate(cursor.description)}

def safe_number(v):
    if v in (None, "", "NULL"): return None
    try: return float(v)
    except: 
        try: return int(v)
        except: return None

app = FastAPI(title="sqliteapi", version="0.1.0")

@app.on_event("startup")
def _startup():
    init_db()

@app.get("/health")
def health():
    # Asegura que exista el .sqlite y devuelve la ruta absoluta
    p = init_db()
    return {"status": "ok", "db": os.path.abspath(p)}

@app.post("/ingest")
def ingest(rows: List[Dict[str, Any]] = Body(...)):
    if not rows:
        return {"status": "empty", "inserted": 0}
    first = rows[0]
    load_date = first.get("load_date") or datetime.utcnow().strftime("%Y-%m-%d")
    source = first.get("source_file_name") or "ads_spend.csv"

    norm: List[Tuple] = []
    for r in rows:
        norm.append((
            r.get("date"),
            r.get("platform"),
            r.get("account"),
            r.get("campaign"),
            r.get("country"),
            r.get("device"),
            safe_number(r.get("spend")),
            safe_number(r.get("clicks")),
            safe_number(r.get("impressions")),
            safe_number(r.get("conversions")),
            r.get("load_date") or load_date,
            r.get("source_file_name") or source
        ))
    with get_conn() as con:
        cur = con.cursor()
        cur.execute("DELETE FROM ads_spend WHERE load_date = ? AND source_file_name = ?", (load_date, source))
        cur.executemany("""
            INSERT INTO ads_spend (
              date,platform,account,campaign,country,device,
              spend,clicks,impressions,conversions,load_date,source_file_name
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
        """, norm)
        con.commit()
    return {"status":"ok","inserted":len(norm),"load_date":load_date,"source":source}

@app.get("/metrics")
def metrics(start: Optional[str] = Query(None), end: Optional[str] = Query(None), compare: Optional[str] = Query(None)):
    if compare == "last30_prev30":
        with get_conn(dict_factory) as con:
            cur = con.cursor()
            b = cur.execute("""
                WITH b AS (SELECT MAX(date) AS maxd FROM ads_spend)
                SELECT maxd AS max_date,
                       date(maxd,'-30 day') AS last_start,
                       date(maxd,'-60 day') AS prev_start,
                       date(maxd,'-30 day') AS prev_end
                FROM b;
            """).fetchone()
            if not b or not b.get("max_date"):
                return {"status":"ok","result":None}
            q = f"""
            WITH last AS (
              SELECT SUM(spend) AS spend, SUM(conversions) AS conv
              FROM ads_spend WHERE date > '{b["last_start"]}' AND date <= '{b["max_date"]}'
            ),
            prev AS (
              SELECT SUM(spend) AS spend, SUM(conversions) AS conv
              FROM ads_spend WHERE date > '{b["prev_start"]}' AND date <= '{b["prev_end"]}'
            )
            SELECT
              (SELECT spend FROM last) AS last_spend,
              (SELECT conv  FROM last) AS last_conv,
              (SELECT CASE WHEN (SELECT conv FROM last) IS NULL OR (SELECT conv FROM last)=0 THEN NULL ELSE (SELECT spend FROM last)*1.0/(SELECT conv FROM last) END) AS last_cac,
              (SELECT CASE WHEN (SELECT spend FROM last) IS NULL OR (SELECT spend FROM last)=0 THEN NULL ELSE (SELECT conv FROM last)*100.0/(SELECT spend FROM last) END) AS last_roas,
              (SELECT spend FROM prev) AS prev_spend,
              (SELECT conv  FROM prev) AS prev_conv,
              (SELECT CASE WHEN (SELECT conv FROM prev) IS NULL OR (SELECT conv FROM prev)=0 THEN NULL ELSE (SELECT spend FROM prev)*1.0/(SELECT conv FROM prev) END) AS prev_cac,
              (SELECT CASE WHEN (SELECT spend FROM prev) IS NULL OR (SELECT spend FROM prev)=0 THEN NULL ELSE (SELECT conv FROM prev)*100.0/(SELECT spend FROM prev) END) AS prev_roas;
            """
            r = cur.execute(q).fetchone() or {}
            def pct(a,b):
                if a is None or b is None or b==0: return None
                return (a-b)/b
            out = {
              "last_30d": {"spend": r.get("last_spend"), "conversions": r.get("last_conv"),
                           "cac": r.get("last_cac"), "roas": r.get("last_roas")},
              "prev_30d": {"spend": r.get("prev_spend"), "conversions": r.get("prev_conv"),
                           "cac": r.get("prev_cac"), "roas": r.get("prev_roas")}
            }
            out["delta_pct"] = {
              "spend": pct(out["last_30d"]["spend"], out["prev_30d"]["spend"]),
              "conversions": pct(out["last_30d"]["conversions"], out["prev_30d"]["conversions"]),
              "cac": pct(out["last_30d"]["cac"], out["prev_30d"]["cac"]),
              "roas": pct(out["last_30d"]["roas"], out["prev_30d"]["roas"])
            }
            return {"status":"ok","result":out}

    if not (start and end):
        return {"status":"error","detail":"Provide start & end or compare=last30_prev30"}

    with get_conn(dict_factory) as con:
        cur = con.cursor()
        r = cur.execute("""
            WITH agg AS (
              SELECT SUM(spend) AS spend, SUM(conversions) AS conv
              FROM ads_spend WHERE date >= ? AND date <= ?
            )
            SELECT spend,
                   conv,
                   CASE WHEN conv IS NULL OR conv=0 THEN NULL ELSE spend*1.0/conv END AS cac,
                   CASE WHEN spend IS NULL OR spend=0 THEN NULL ELSE conv*100.0/spend END AS roas
            FROM agg;
        """, (start, end)).fetchone() or {}
    return {"status":"ok","range":{"start":start,"end":end},
            "spend": r.get("spend"), "conversions": r.get("conv"),
            "cac": r.get("cac"), "roas": r.get("roas")}
