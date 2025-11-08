
# Workshop3 – EDA (offline) + Kafka Streaming + Model Serving

## Setup
```bash
python -m venv .venv
. .venv/Scripts/Activate.ps1   # Windows
# source .venv/bin/activate    # Linux/macOS
pip install -r requirements.txt
```
Place `2015.csv` … `2019.csv` in `data/data_raw/`.

## Run
1) `python src/eda.py`
2) `python src/build_dataset.py`
3) `python src/train.py`
4) Start Kafka, then:
   - Terminal A: `python src/consumer.py`
   - Terminal B: `python src/producer.py`
