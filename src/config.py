from dotenv import load_dotenv
import os
load_dotenv()

EX_API_BASE = os.getenv("EXCHANGE_API_BASE")
EX_API_KEY  = os.getenv("EXCHANGE_API_KEY")
BASE_CUR    = os.getenv("BASE_CURRENCY", "BRL")

DATA_DIR    = "data"
RAW_DIR     = f"{DATA_DIR}/raw"
SILVER_DIR  = f"{DATA_DIR}/silver"
GOLD_DIR    = f"{DATA_DIR}/gold"

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "none")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

PG = {
    "host": os.getenv("PGHOST"),
    "port": int(os.getenv("PGPORT", "5432")),
    "db": os.getenv("PGDATABASE"),
    "user": os.getenv("PGUSER"),
    "pwd": os.getenv("PGPASSWORD"),
}
