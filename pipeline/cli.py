from random import randint, random

import typer
from config import logger

from mlflow import log_metric, log_param

app = typer.Typer()


@app.command()
def extract_data():
    logger.info("Extracting Data!")


@app.command()
def test_mlflow():
    # Log a parameter (key-value pair)
    log_param("param1", randint(0, 100))

    # Log a metric; metrics can be updated throughout the run
    log_metric("foo", random())
    log_metric("foo", random() + 1)
    log_metric("foo", random() + 2)


if __name__ == "__main__":
    app()
