from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel
from rich.pretty import Pretty

from fastrag import DEFAULT_CONFIG
from fastrag.config import Config, ConfigLoader, Steps
from fastrag.utils import version

app = typer.Typer(help="CLI RAG generator")
console = Console()


@app.command()
def main(
    config: Annotated[
        Path,
        typer.Argument(help="Path to the config file."),
    ] = DEFAULT_CONFIG,
    plugins: Annotated[
        Path | None,
        typer.Argument(help="Path to the plugins directory."),
    ] = None,
    step: Annotated[
        str,
        typer.Argument(
            help="What step to execute up to",
        ),
    ] = "all",
):
    """
    Go through the process of generating a fastRAG.
    """

    console.print(
        Panel.fit(
            f"[bold cyan]fastrag[/bold cyan] [green]v{version("fastrag")}[/green]",
            border_style="cyan",
        ),
        justify="center",
    )

    # Load plugins before config
    load_plugins(plugins)
    config: Config = load_config(config)
    run(config.steps)


def load_config(config: Path) -> Config:
    if config == DEFAULT_CONFIG:
        console.print(":scroll: Using [bold magenta]DEFAULT[/bold magenta] config path")
    else:
        console.print(
            f":scroll: [bold yellow]Loading config from[/bold yellow] {config!r}"
        )
    config: Config = ConfigLoader.from_settings(config)
    console.print(
        Panel(
            Pretty(config),
            title="Loaded Configuration",
            border_style="yellow",
        )
    )
    return config


def load_plugins(plugins: Path) -> None:
    from fastrag.plugins import import_path, plugin_registry

    if plugins is not None:
        import_path(plugins)

    console.print(
        Panel(
            Pretty(plugin_registry),
            title="Plugin Registry",
            border_style="green",
        )
    )


def run(steps: Steps) -> None: ...


if __name__ == "__main__":
    app()
