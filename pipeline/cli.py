import typer
from config import logger

app = typer.Typer()


@app.command()
def extract_data():
    logger.info("Extracting Data!")


if __name__ == "__main__":
    app()
