from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel
from rich.pretty import Pretty

from fastrag import DEFAULT_CONFIG
from fastrag.config import Config, ConfigLoader
from fastrag.utils import version

app = typer.Typer(help="CLI RAG generator")
console = Console()


@app.command()
def main(
    config: Annotated[
        Path,
        typer.Argument(help="Path to the config file."),
    ] = DEFAULT_CONFIG,
):
    """
    Go through the process of generating a fastRAG.
    """

    console.print(
        Panel.fit(
            f"[bold cyan]fastrag[/bold cyan] [green]v{version("fastrag")}[/green]",
            border_style="cyan",
        )
    )

    config = load_config(config)
    load_plugins(config)


def load_config(config: Path) -> Config:
    if config == DEFAULT_CONFIG:
        console.print("Using [bold magenta]DEFAULT[/bold magenta] config path")
    else:
        console.print(
            f":scroll: [bold yellow]Loading config from[/bold yellow] {config!r}"
        )
    config: Config = ConfigLoader.from_settings(config)
    console.print(Pretty(config))
    return config


def load_plugins(config: Config):
    from fastrag.plugins import import_path, plugin_registry

    import_path(config.plugins)

    console.print(
        Panel(
            Pretty(plugin_registry),
            title="Plugin Registry",
            border_style="green",
        )
    )


if __name__ == "__main__":
    app()
