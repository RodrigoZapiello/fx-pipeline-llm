import os, pandas as pd
from src.load import write_gold

def test_write_gold(tmp_path):
    df = pd.DataFrame({"currency":["USD"],"rate":[5.0],"base_currency":["BRL"],"timestamp":[pd.Timestamp("2024-01-01")]})
    old = os.getcwd()
    try:
        os.chdir(tmp_path)
        os.makedirs("data/gold", exist_ok=True)
        p = write_gold(df)
        assert os.path.exists(p)
    finally:
        os.chdir(old)
