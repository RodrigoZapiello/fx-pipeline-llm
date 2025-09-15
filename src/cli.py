import typer
from .config import settings
from .logging_conf import setup_logging
from . import ingest, transform, load

app = typer.Typer(help="fx-pipeline-llm CLI")

@app.callback()
def main(log_level: str = settings.log_level):
    setup_logging(log_level)

@app.command()       # python -m src.cli ingest
def ingest_cmd(): ingest.run(settings)

@app.command()       # python -m src.cli transform
def transform_cmd(): transform.run(settings)

@app.command()       # python -m src.cli load
def load_cmd(): load.run(settings)

@app.command()       # python -m src.cli all
def all(): ingest.run(settings); transform.run(settings); load.run(settings)

if __name__ == "__main__":
    app()
