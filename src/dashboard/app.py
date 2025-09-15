import streamlit as st, pandas as pd, os, glob

GOLD_DIR = "data/gold"

st.set_page_config(page_title="FX Dashboard", layout="wide")

@st.cache_data
def load_data():
    p = os.path.join(GOLD_DIR, "rates.parquet")
    if not os.path.exists(p):
        return pd.DataFrame()
    return pd.read_parquet(p)

def latest_insight():
    files = sorted(glob.glob(os.path.join(GOLD_DIR, "insights_*.md")))
    if not files:
        return "Sem insights ainda."
    with open(files[-1], "r", encoding="utf-8") as f:
        return f.read()

df = load_data()
st.title("📈 FX Dashboard (BRL)")

if df.empty:
    st.warning("Sem dados. Rode o pipeline primeiro.")
else:
    latest = df.groupby("currency").tail(1).sort_values("rate", ascending=False)
    st.subheader("Top 10 moedas (hoje)")
    st.dataframe(latest[["rate","base_currency","timestamp"]].head(10))

    st.subheader("Distribuição de taxas (todos os registros)")
    st.bar_chart(df[["currency","rate"]].set_index("currency").sort_values("rate").tail(20))

st.subheader("🧠 Insight do dia")
st.markdown(latest_insight())
