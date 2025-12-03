from pathlib import Path
from typing import Annotated

import typer

from fastrag.config import Config

app = typer.Typer(help="CLI RAG generator")


@app.command()
def main(
    config: Annotated[
        Path,
        typer.Option(
            prompt="What is the path of the config YAML?",
            help="Path to the config file.",
        ),
    ] = Path("config.yaml"),
):
    """
    Go through the process of generating a fastRAG.
    """

    if config.exists():
        print(f"Loading config from '{config.absolute()}'")
    else:
        raise ValueError(f"Could not find config file at {config.absolute()}")

    config = Config().from_yaml(config)


if __name__ == "__main__":
    app()
