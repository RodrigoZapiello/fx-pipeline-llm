import os, pandas as pd, datetime as dt
from .config import GOLD_DIR, LLM_PROVIDER, OPENAI_API_KEY, BASE_CUR
from .logging_conf import setup_logging

log = setup_logging()

PROMPT = """Você é um analista financeiro. Com base no dataset abaixo (moeda, taxa, base, timestamp),
explique em termos simples como está a variação das 5 principais moedas frente ao {base} hoje.
Destaque:
- moeda mais valorizada e mais desvalorizada vs ontem
- variação percentual média do G10
- 1 insight executivo para diretoria
"""

def load_gold():
    return pd.read_parquet(f"{GOLD_DIR}/rates.parquet")

def build_context(df: pd.DataFrame):
    latest = df.groupby("currency").tail(1).set_index("currency")
    top = latest.sort_values("rate", ascending=False).head(5)[["rate","base_currency","timestamp"]]
    return top.to_csv()

def call_llm(prompt: str, context: str) -> str:
    if LLM_PROVIDER != "openai" or not OPENAI_API_KEY:
        return "LLM desativado (sem chave)."
    from openai import OpenAI
    client = OpenAI(api_key=OPENAI_API_KEY)
    msg = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role":"system","content":"Responda em PT-BR, claro e objetivo."},
            {"role":"user","content": prompt + "\n\nDataset CSV:\n" + context}
        ],
        temperature=0.2
    )
    return msg.choices[0].message.content.strip()

def run():
    df = load_gold()
    ctx = build_context(df)
    txt = call_llm(PROMPT.format(base=BASE_CUR), ctx)
    path = f"{GOLD_DIR}/insights_{dt.date.today().isoformat()}.md"
    with open(path, "w", encoding="utf-8") as f:
        f.write(txt)
    log.info("llm_summary_saved", file=path)

if __name__ == "__main__":
    run()
