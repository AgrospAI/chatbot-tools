from pathlib import Path
from typing import Annotated

import typer

from fastrag.config import Config, ConfigLoader
from fastrag.plugins import plugin_registry

app = typer.Typer(help="CLI RAG generator")


@app.command()
def main(
    config: Annotated[
        Path,
        typer.Argument(help="Path to the config file."),
    ] = Path("config.yaml"),
):
    """
    Go through the process of generating a fastRAG.
    """

    if config.exists():
        print(f"Loading config from '{config.absolute()}'")
    else:
        raise ValueError(f"Could not find config file at {config.absolute()}")

    print(plugin_registry)
    config: Config = ConfigLoader.from_settings(config)


if __name__ == "__main__":
    app()
