import requests, os, json, datetime as dt
from .config import EX_API_BASE, EX_API_KEY, BASE_CUR, RAW_DIR
from .logging_conf import setup_logging

log = setup_logging()

def fetch_rates(base=BASE_CUR):
    if not EX_API_BASE or not EX_API_KEY:
        raise RuntimeError("EXCHANGE_API_BASE/EXCHANGE_API_KEY não definidos (.env).")
    url = f"{EX_API_BASE}/{EX_API_KEY}/latest/{base}"
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    return resp.json()

def save_raw(payload: dict, when=None):
    os.makedirs(RAW_DIR, exist_ok=True)
    if when is None:
        when = dt.date.today()
    fname = f"{RAW_DIR}/{when.isoformat()}.json"
    with open(fname, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False)
    log.info("raw_saved", file=fname, base_currency=payload.get("base_code"))
    return fname

def run():
    data = fetch_rates()
    if "conversion_rates" not in data:
        raise ValueError("Resposta sem 'conversion_rates'")
    save_raw(data)
    log.info("ingest_ok")

if __name__ == "__main__":
    run()
