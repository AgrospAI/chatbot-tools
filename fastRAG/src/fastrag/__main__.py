from pathlib import Path
import shutil
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel
from rich.pretty import Pretty

from fastrag import (
    DEFAULT_CONFIG,
    Config,
    IConfigLoader,
    IStepRunner,
    init_constants,
    version,
    Constants,
)

app = typer.Typer(help="CLI RAG generator", add_completion=False)
console = Console()


@app.command()
def clean(
    sure: Annotated[
        bool,
        typer.Option(prompt="Are you sure you want to continue?"),
    ] = True,
):
    """Clean the caches"""

    if not sure:
        return

    with open(Constants.global_cache()) as f:
        lines = f.readlines()
        for path in lines:
            shutil.rmtree(path)

        Constants.global_cache().unlink()


@app.command()
def run(
    step: Annotated[
        int,
        typer.Argument(
            help="What step to execute up to",
        ),
    ] = -1,
    config: Annotated[
        Path,
        typer.Argument(help="Path to the config file."),
    ] = DEFAULT_CONFIG,
    plugins: Annotated[
        Path | None,
        typer.Option("--plugins", "-p", help="Path to the plugins directory."),
    ] = None,
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

    IStepRunner.run(config, step)


def load_config(path: Path) -> Config:
    config: Config = IConfigLoader.from_settings(path)
    init_constants(config)
    console.print(
        Panel(
            Pretty(config),
            title="[bold]Loaded Configuration[/bold]",
            subtitle=(
                ":scroll: Using [bold magenta]DEFAULT[/bold magenta] config path"
                if config == DEFAULT_CONFIG
                else f":scroll: [bold yellow]Loaded from[/bold yellow] {path!r}"
            ),
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
            title="[bold]Plugin Registry[/bold]",
            border_style="green",
        )
    )


if __name__ == "__main__":
    app()
