# Workshop 3 – Offline EDA + ML Pipeline + Kafka Streaming

This repository contains an end-to-end mini data engineering & MLOps workflow:

1. **Offline pipeline**: data cleaning, unification, feature engineering, model training and evaluation.
2. **Streaming pipeline**: real-time inference using **Apache Kafka** (producer + consumer).
3. **Storage for analytics**: predictions persisted into **SQLite** for easy connection to BI tools (Power BI, Looker Studio, etc.).

The project is built around the **World Happiness** datasets (2015–2019) and demonstrates how to move from raw CSV files to a production-like streaming architecture.

---

## 1. Project Structure

```bash
Workshop3_starter/
├─ src/
│  ├─ run_offline_pipeline.py   # EDA, data cleaning, feature engineering, model training
│  ├─ producer.py               # Kafka producer: sends records & model predictions
│  ├─ consumer.py               # Kafka consumer: receives predictions, stores in SQLite
├─ data/
│  ├─ data_raw/                 # Input CSV files (2015–2019)
│  ├─ eda_out/                  # EDA tables & charts generated offline
│  ├─ preds.db                  # SQLite DB with predictions table (created by consumer)
├─ models/
│  ├─ model.pkl                 # Trained Ridge regression model (generated offline)
├─ artifacts/
│  ├─ dataset_unified.csv       # Unified cleaned dataset
│  ├─ features_used.csv         # Final features used by the model
│  ├─ metrics.json              # Model metrics (R², RMSE, MAE, etc.)
│  ├─ diag_y_pred_vs_y_true.png # Diagnostic plot for predictions
├─ docker-compose.yml           # Kafka + Zookeeper stack
├─ requirements.txt
├─ .env                         # Environment variables (local only, not committed)
└─ README.md

```
## 2. Dataset Description

The project uses yearly World Happiness-style datasets for:

2015.csv to 2019.csv in data/data_raw/

During the offline pipeline, the script:

Normalizes column names (lowercase, snake_case).

Unifies variations such as:

country, country_or_region, country_name

happiness_score, score, etc.

Casts numeric columns safely (GDP, social support, freedom, etc.).

Adds the year column when missing.

Generates a unified, clean dataset: artifacts/dataset_unified.csv.

This unified dataset becomes the single source of truth for training and streaming.

3. Offline Pipeline (EDA + Training)

Run the complete offline workflow:
python -m venv .venv
# Windows
. .venv/Scripts/Activate.ps1
# Linux/macOS
# source .venv/bin/activate

pip install -r requirements.txt

python src/run_offline_pipeline.py


This script:

Loads all raw CSVs (2015–2019).

Cleans and standardizes schemas.

Generates EDA outputs in data/eda_out/, such as:

Missing values by year

Distributions and trends of happiness score

Top/bottom countries per year

Splits the data into train/test (configurable via constants).

Trains a Ridge Regression model with cross-validation.

Evaluates the model and saves:

artifacts/model.pkl – serialized model

artifacts/features_used.csv – final feature set

artifacts/metrics.json – metrics (R², RMSE, MAE, etc.)

artifacts/diag_y_pred_vs_y_true.png – diagnostic chart

These artifacts are later reused by the streaming components.

4. Environment Configuration (.env)

Create a .env file in the project root:

# Kafka
KAFKA_BROKERS=localhost:9092
KAFKA_TOPIC=workshop3.happiness

# Offline artifacts
MODEL_BUNDLE=models/model.pkl
DATASET_CSV=artifacts/dataset_unified.csv

# SQLite output for predictions
SQLITE_PATH=data/preds.db
SQLITE_TABLE=predictions

# Train/test config (must match offline pipeline)
RANDOM_STATE=42
TEST_SIZE=0.30

# Producer behavior
SEND_ONLY_TEST=true

Adjust values as needed.
This allows producer & consumer to stay in sync with your offline training.

5. Start Kafka with Docker

To run Kafka and Zookeeper locally:

docker-compose up -d

This will start:

wk3-zookeeper on 2181

wk3-kafka on 9092 (exposed as localhost:9092)

Ensure Docker is running before starting the streaming pipeline.

6. Streaming Pipeline (Real-Time Inference)
6.1. Run the Consumer (sink → SQLite)

The consumer listens to the Kafka topic and writes predictions to SQLite:

python src/consumer.py

It will:

Load the trained model (model.pkl).

Subscribe to KAFKA_TOPIC.

For each message (country + features + prediction), insert a row into:

data/preds.db, table predictions.

6.2. Run the Producer (source → Kafka)

In another terminal (same venv activated):

python src/producer.py

It will:

Read dataset_unified.csv.

Rebuild the same train/test split used offline.

Optionally send only the test set (controlled by SEND_ONLY_TEST).

For each record, compute a prediction using model.pkl.

Publish messages to the Kafka topic defined in .env.

Once both are running, you have:

End-to-end loop: clean data → trained model → live predictions over Kafka → stored in SQLite for analytics.

7. Consuming Predictions from SQLite

After running producer + consumer, you can inspect results, for example:

python
>>> import sqlite3, pandas as pd
>>> con = sqlite3.connect("data/preds.db")
>>> df = pd.read_sql_query("SELECT * FROM predictions LIMIT 10", con)
>>> df.head()

You can connect data/preds.db directly from:

Power BI

Tableau

Looker Studio (via connector)

Any analytics tool that supports SQLite.

8. Technologies Used

Python 3.11+

Pandas, NumPy, Matplotlib

Scikit-learn (Ridge Regression, CV, metrics)

Apache Kafka (via kafka-python)

Docker & Docker Compose

SQLite for lightweight storage

This workshop is designed as a practical template to understand how offline ML, streaming, and analytics can work together in a simple but production-like architecture.

9. How to Run Everything (Quick Start)

Clone the repo.

Create & activate virtual environment.

Install dependencies: pip install -r requirements.txt

(If needed) Place raw CSVs into data/data_raw/.

Run python src/run_offline_pipeline.py

Start Kafka: docker-compose up -d

Run python src/consumer.py

Run python src/producer.py

Explore data/preds.db in your BI tool of choice.

10. Notes

Do not commit .env, local databases, or large raw data.

The configuration values in .env must stay consistent with the offline pipeline.

This repo is intentionally minimal but realistic, to be extended in future workshops (monitoring, CI/CD, model registry, etc.).

