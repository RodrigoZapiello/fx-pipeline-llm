from src.ingest import save_raw
import os

def test_save_raw(tmp_path):
    payload = {"base_code":"BRL","conversion_rates":{"USD":5.0}}
    old = os.getcwd()
    try:
        os.chdir(tmp_path)
        os.makedirs("data/raw", exist_ok=True)
        fname = save_raw(payload)
        assert os.path.exists(fname)
    finally:
        os.chdir(old)
