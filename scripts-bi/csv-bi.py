# scripts-bi/csv-bi.py

import os
import json
import sqlite3
from pathlib import Path

import pandas as pd

# =========================
# CONFIGURACIÓN DE RUTAS
# =========================

# Carpeta raíz del proyecto (sube un nivel desde scripts-bi)
ROOT_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = ROOT_DIR / "data"
ARTIFACTS_DIR = ROOT_DIR / "artifacts"

DB_PATH = DATA_DIR / "preds.db"
PREDICTIONS_CSV_PATH = DATA_DIR / "predictions.csv"
METRICS_JSON_PATH = ARTIFACTS_DIR / "metrics.json"
METRICS_CSV_PATH = ARTIFACTS_DIR / "metrics_for_bi.csv"

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(ARTIFACTS_DIR, exist_ok=True)

# =========================
# 1) EXPORTAR PREDICTIONS
# =========================

if not DB_PATH.exists():
    raise FileNotFoundError(f"No se encontró la base de datos: {DB_PATH}")

con = sqlite3.connect(DB_PATH)

try:
    df = pd.read_sql_query("SELECT * FROM predictions", con)
except Exception as e:
    con.close()
    raise RuntimeError(f"Error al leer la tabla 'predictions' desde {DB_PATH}: {e}")

# Tipos recomendados para Power BI
for c in ("year", "is_train", "is_test"):
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce").astype("Int64")

for c in ("actual", "prediction", "error_abs", "prob_up", "prob_down"):
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")

df.to_csv(PREDICTIONS_CSV_PATH, index=False, encoding="utf-8")
print(f"OK -> {PREDICTIONS_CSV_PATH} ({len(df)} filas)")

# =========================
# 2) EXPORTAR MÉTRICAS
# =========================

if not METRICS_JSON_PATH.exists():
    print(f"ADVERTENCIA: No se encontró {METRICS_JSON_PATH}, no se exportan métricas.")
else:
    with open(METRICS_JSON_PATH, "r", encoding="utf-8") as f:
        metrics = json.load(f)

    if isinstance(metrics, dict):
        mdf = pd.DataFrame([metrics])
    else:
        mdf = pd.DataFrame(metrics)

    mdf.to_csv(METRICS_CSV_PATH, index=False, encoding="utf-8")
    print(f"OK -> {METRICS_CSV_PATH}")

con.close()
