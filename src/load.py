import os, pandas as pd
from sqlalchemy import create_engine
from .config import SILVER_DIR, GOLD_DIR, PG
from .logging_conf import setup_logging

log = setup_logging()

def concat_silver():
    files = [os.path.join(SILVER_DIR, f) for f in os.listdir(SILVER_DIR) if f.endswith(".parquet")]
    if not files:
        raise FileNotFoundError("Sem arquivos em silver/")
    return pd.concat([pd.read_parquet(f) for f in sorted(files)], ignore_index=True)

def write_gold(df):
    os.makedirs(GOLD_DIR, exist_ok=True)
    p = f"{GOLD_DIR}/rates.parquet"
    df.to_parquet(p, index=False)
    log.info("gold_saved", file=p, rows=len(df))
    return p

def to_postgres(df):
    if not all(PG.values()):
        log.info("postgres_skip", reason="vars ausentes"); return
    url = f"postgresql://{PG['user']}:{PG['pwd']}@{PG['host']}:{PG['port']}/{PG['db']}"
    eng = create_engine(url)
    with eng.begin() as con:
        con.exec_driver_sql("""
            CREATE TABLE IF NOT EXISTS rates(
                currency TEXT, rate DOUBLE PRECISION, base_currency TEXT, timestamp TIMESTAMP
            )""")
        df.to_sql("rates", con=con, if_exists="append", index=False)
    log.info("postgres_loaded", rows=len(df))

def run():
    df = concat_silver()
    p = write_gold(df)
    to_postgres(df)
    log.info("load_ok", gold=p)

if __name__ == "__main__":
    run()
