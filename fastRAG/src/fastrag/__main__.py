from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel
from rich.pretty import Pretty

from fastrag import DEFAULT_CONFIG, Config, ConfigLoader
from fastrag.steps.steps import StepRunner
from fastrag.helpers.utils import version

app = typer.Typer(help="CLI RAG generator")
console = Console()


@app.command()
def main(
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
        typer.Argument(help="Path to the plugins directory."),
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

    StepRunner.run(config.steps, step)


def load_config(path: Path) -> Config:
    config: Config = ConfigLoader.from_settings(path)
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
