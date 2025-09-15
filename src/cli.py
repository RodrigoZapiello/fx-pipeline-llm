import typer
from .ingest import run as ingest_run
from .transform import run as transform_run
from .load import run as load_run
from .llm_summarize import run as llm_run

app = typer.Typer(help="FX Pipeline + LLM")

@app.command()
def run_all():
    ingest_run()
    transform_run()
    load_run()
    llm_run()

@app.command()
def ingest():
    ingest_run()

@app.command()
def transform():
    transform_run()

@app.command()
def load():
    load_run()

@app.command()
def insights():
    llm_run()

if __name__ == "__main__":
    app()
