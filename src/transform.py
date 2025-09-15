import json, os, pandas as pd, datetime as dt
from .config import RAW_DIR, SILVER_DIR
from .logging_conf import setup_logging

log = setup_logging()

def latest_raw_path():
    files = sorted([f for f in os.listdir(RAW_DIR) if f.endswith(".json")])
    if not files:
        raise FileNotFoundError("Sem arquivos em raw/")
    return os.path.join(RAW_DIR, files[-1])

def normalize(path):
    with open(path, encoding="utf-8") as f:
        j = json.load(f)
    base = j["base_code"]
    ts = pd.to_datetime(j.get("time_last_update_utc"))
    rows = [{
        "currency": c,
        "rate": float(r),
        "base_currency": base,
        "timestamp": ts
    } for c, r in j["conversion_rates"].items()]
    df = pd.DataFrame(rows)
    df = df[df["rate"].notna() & (df["rate"] > 0)]
    return df

def write_silver(df: pd.DataFrame, when=None):
    os.makedirs(SILVER_DIR, exist_ok=True)
    if when is None:
        when = dt.date.today()
    p = f"{SILVER_DIR}/{when.isoformat()}.parquet"
    df.to_parquet(p, index=False)
    log.info("silver_saved", file=p, rows=len(df))
    return p

def run():
    p = latest_raw_path()
    df = normalize(p)
    write_silver(df)
    log.info("transform_ok")

if __name__ == "__main__":
    run()
