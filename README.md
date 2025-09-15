
# FX Pipeline + LLM (BRL)

Pipeline de cotações cambiais com camadas **raw → silver → gold**, **insights diários** (via LLM opcional) e **dashboard Streamlit**. Empacotado em **Docker/Compose**, com **testes** e **CI no GitHub Actions**.

> **Highlights**
> - ETL de câmbio com dados persistidos em **Parquet**  
> - **Dashboard** (Streamlit) com Top moedas + distribuição  
> - **Insight do dia** (LLM OpenAI opcional, com fallback local)  
> - **Logging estruturado** (JSON) e **testes** (pytest)  
> - **Postgres** opcional via Compose  
> - **CI**: testes em PR e agendamento diário de execução

---

## Sumário
- [Arquitetura](#arquitetura)
- [Estrutura de Pastas](#estrutura-de-pastas)
- [Pré-requisitos](#pré-requisitos)
- [Configuração do Ambiente (.env)](#configuração-do-ambiente-env)
- [Como Rodar](#como-rodar)
  - [Com Docker (recomendado)](#com-docker-recomendado)
  - [Sem Docker (venv local)](#sem-docker-venv-local)
- [Comandos Essenciais](#comandos-essenciais)
- [Dashboard](#dashboard)
- [Insight do Dia (LLM)](#insight-do-dia-llm)
- [Testes](#testes)
- [Banco de Dados (opcional)](#banco-de-dados-opcional)
- [CI no GitHub Actions](#ci-no-github-actions)
- [Segurança](#segurança)
- [Solução de Problemas (FAQ)](#solução-de-problemas-faq)
- [Roadmap / Ideias de Evolução](#roadmap--ideias-de-evolução)
- [Licença](#licença)

---

## Arquitetura

```
          ┌──────────────┐        ┌──────────────┐        ┌─────────────┐
API FX →  │  RAW (JSON)  │  ETL   │ SILVER (PQ)  │  ETL   │  GOLD (PQ)  │
          └──────┬───────┘        └──────┬───────┘        └──────┬──────┘
                 │                       │                       │
                 │                       │                       ├──▶ insights_YYYY-MM-DD.md (LLM ou fallback)
                 │                       │                       └──▶ rates.parquet
                 │                       │
                 │                       └───────────────────────────────────────┐
                 │                                                               │
                 └───────────────────────────────────────────────────────────────┼──▶ Dashboard (Streamlit)
                                                                                 │
                                                                                 └──▶ Postgres (opcional)
```

- **RAW**: resposta bruta da API (`data/raw/YYYY-MM-DD.json`)  
- **SILVER**: dados normalizados/validados (`data/silver/YYYY-MM-DD.parquet`)  
- **GOLD**: conjunto consolidado para consumo analítico (`data/gold/rates.parquet`) + **insight diário** (`data/gold/insights_*.md`)  
- **LLM**: gera resumo executivo (opcional; com fallback local para não quebrar)  
- **Dashboard**: visualizações simples e rápidas (Streamlit)

---

## Estrutura de Pastas
```
fx-pipeline-llm/
├─ .github/workflows/ci.yml
├─ .env.example
├─ .gitignore
├─ Dockerfile
├─ docker-compose.yml
├─ Makefile
├─ README.md
├─ requirements.txt
├─ .streamlit/               # opcional: config.toml do Streamlit
│  └─ config.toml
├─ data/
│  ├─ raw/
│  ├─ silver/
│  └─ gold/
├─ src/
│  ├─ __init__.py
│  ├─ config.py
│  ├─ logging_conf.py
│  ├─ ingest.py
│  ├─ transform.py
│  ├─ load.py
│  ├─ llm_summarize.py
│  ├─ dashboard/
│  │  └─ app.py
│  └─ cli.py
└─ tests/
   ├─ test_ingest.py
   ├─ test_transform.py
   └─ test_load.py
```

---

## Pré-requisitos
- **Docker Desktop** (Windows/macOS) com **WSL2** habilitado no Windows  
- **Git**  
- (Opcional) **Python 3.11** + **virtualenv** se for rodar sem Docker  
- **Token da API de câmbio** (exchangerate-api.com)  
- (Opcional) **OPENAI_API_KEY** para o insight via LLM

---

## Configuração do Ambiente (.env)

Crie o arquivo `.env` (nunca comite; já está no `.gitignore`):

```env
# API de câmbio
EXCHANGE_API_BASE=https://v6.exchangerate-api.com/v6
EXCHANGE_API_KEY=SEU_TOKEN_AQUI
BASE_CURRENCY=BRL

# LLM (opcional) — use 'openai' + OPENAI_API_KEY ou 'none'
LLM_PROVIDER=openai
OPENAI_API_KEY=SUA_CHAVE_OPENAI

# Postgres (opcional)
PGHOST=db
PGPORT=5432
PGDATABASE=fx
PGUSER=fx_user
PGPASSWORD=fx_pass
```

> **Dica:** copie de `.env.example` → `.env` e edite os valores.

---

## Como Rodar

### Com Docker (recomendado)

1. **Build**  
   ```bash
   docker compose build
   ```

2. **Executar o pipeline (uma vez)**  
   ```bash
   docker compose run --rm app
   ```
   Isso roda: `ingest → transform → load → insights`

3. **Subir o dashboard**  
   ```bash
   docker compose up dashboard
   ```
   Acesse: http://localhost:8501

> **Windows:** se aparecer “make não reconhecido”, ignore os alvos do Makefile e use os comandos acima.

### Sem Docker (venv local)

```bash
python -m venv .venv
# Windows: .\.venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
# edite .env e coloque seu EXCHANGE_API_KEY (e OPENAI_API_KEY se usar LLM)

python -m src.cli run-all
streamlit run src/dashboard/app.py
```

---

## Comandos Essenciais

**Pipeline completo (Docker):**
```bash
docker compose run --rm app
```

**Passos individuais (Docker):**
```bash
docker compose run --rm app python -m src.cli ingest
docker compose run --rm app python -m src.cli transform
docker compose run --rm app python -m src.cli load
docker compose run --rm app python -m src.cli insights
```

**Dashboard:**
```bash
docker compose up dashboard
# ou em background:
docker compose up -d dashboard
docker compose logs -f dashboard
```

---

## Dashboard

- **Top 10 moedas (hoje)** por taxa vs. BRL  
- **Distribuição de taxas** (últimos registros)  
- **🧠 Insight do dia**: lê `data/gold/insights_*.md` (gerado pelo LLM ou fallback)

> Se quiser personalizar: edite `src/dashboard/app.py` (filtros, gráficos, KPIs).

---

## Insight do Dia (LLM)

- **Com LLM (OpenAI)**  
  No `.env`:
  ```env
  LLM_PROVIDER=openai
  OPENAI_API_KEY=...
  ```
  Gere:
  ```bash
  docker compose run --rm app python -m src.cli insights
  ```

- **Sem LLM**  
  No `.env`:
  ```env
  LLM_PROVIDER=none
  ```
  Gere:
  ```bash
  docker compose run --rm app python -m src.cli insights
  ```
  O arquivo é criado com texto padrão.  
  > Dica: você pode implementar **fallback local** em `llm_summarize.py` (cálculos d/d-1, G10 etc.) para nunca quebrar caso falte cota.

---

## Testes

```bash
docker compose run --rm app pytest -q
# ou local:
pytest -q
```

- `test_ingest.py`: valida o salvamento de RAW  
- `test_transform.py`: garante limpeza/validação (sem taxas <= 0)  
- `test_load.py`: verifica escrita do GOLD Parquet

---

## Banco de Dados (opcional)

O `docker-compose.yml` já traz um **Postgres 16**. Se as variáveis `PG*` estiverem preenchidas no `.env`, o `load.py` cria a tabela `rates` e insere os dados.

- **Conexão padrão:** `postgresql://fx_user:fx_pass@db:5432/fx`  
- **Tabela:** `rates(currency TEXT, rate DOUBLE PRECISION, base_currency TEXT, timestamp TIMESTAMP)`

---

## CI no GitHub Actions

O workflow em `.github/workflows/ci.yml` faz:
- **Testes** em `push` e `pull_request`
- **Execução diária** às **12:00 UTC** (≈ 09:00 América/São_Paulo)

**Configure os Secrets** no repositório (Settings → Secrets and variables → Actions):
- `EXCHANGE_API_BASE = https://v6.exchangerate-api.com/v6`
- `EXCHANGE_API_KEY = <sua_chave>`
- (opcional) `OPENAI_API_KEY = <sua_chave>`

> Os artefatos (GOLD) podem ser publicados no Actions (upload-artifact) para download.

---

## Segurança

- **Nunca** comite `.env` (já ignorado).  
- Se expôs uma chave, **revogue e gere outra**.  
- Use **GitHub Secrets** para a CI.  
- Logs são **estruturados (JSON)** para facilitar auditoria (veja `logging_conf.py`).

---

## Solução de Problemas (FAQ)

**“`make` não reconhecido (Windows)”**  
Use os comandos `docker compose ...` diretamente. `make` é opcional.

**“Docker: cannot connect / engine parado”**  
Abra o **Docker Desktop** e ative **WSL2** (Windows). Verifique `docker info`.

**“Streamlit: TomlDecodeError no `config.toml`”**  
Crie `.streamlit/config.toml` válido:
```toml
[server]
headless = true
port = 8501
address = "0.0.0.0"
```
Monte essa pasta no serviço `dashboard` em `docker-compose.yml`:
```yaml
    volumes:
      - ./.streamlit:/home/appuser/.streamlit:ro
      - ./.streamlit:/app/.streamlit:ro
```

**“LLM: 429 insufficient_quota / free account”**  
A API requer **crédito**. Adicione billing na OpenAI **ou** use `LLM_PROVIDER=none`.  
(O projeto pode ter fallback local em `llm_summarize.py` para nunca quebrar.)

**“Porta 8501 ocupada”**  
Altere a porta em `docker-compose.yml` (ex.: `"8502:8501"`) e acesse `localhost:8502`.

---

## Roadmap / Ideias de Evolução

- **Histórico e variações** d/d-1, d-7, MTD / YTD por moeda  
- **Filtros** (G10, LatAm, custom watchlist) e **gráficos de linha**  
- **Alertas** (ex.: variação > X%) via e-mail/Slack  
- **Qualidade de dados**: testes de contrato de schema, regras de outlier  
- **Metrics & observabilidade**: Prometheus/Grafana ou logs centralizados  
- **Databricks / Delta Lake** para camadas com versionamento e ACID  
- **Export** para BI (Parquet → Lakehouse → Metabase/Power BI)

---

## Licença

Sugerido: **MIT** (ajuste conforme sua necessidade).
