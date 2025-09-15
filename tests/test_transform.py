import json, pandas as pd
from src.transform import normalize

def test_normalize_filters_invalid(tmp_path):
    j = {"base_code":"BRL","time_last_update_utc":"Mon, 01 Jan 2024 00:00:00 +0000",
         "conversion_rates":{"USD":5.0,"XXX":-1}}
    p = tmp_path / "x.json"
    p.write_text(json.dumps(j), encoding="utf-8")
    df = normalize(str(p))
    assert "USD" in df["currency"].values
    assert "XXX" not in df["currency"].values
    assert (df["rate"] > 0).all()
