from pathlib import Path

import typer
from rich.panel import Panel
from rich.pretty import Pretty

from fastrag import (
    DEFAULT_CONFIG,
    PluginRegistry,
    import_plugins,
)
from fastrag.commands.clean import app as clean_app
from fastrag.commands.run import app as run_app
from fastrag.commands.serve import app as serve_app
from fastrag.config.config import get_config, get_resources
from fastrag.console import console
from fastrag.context import AppContext

app = typer.Typer(help="FastRAG CLI", add_completion=False)

app.add_typer(run_app)
app.add_typer(serve_app)
app.add_typer(clean_app)


@app.callback()
def main(
    ctx: typer.Context,
    config_path: Path = typer.Option(
        DEFAULT_CONFIG,
        "--config",
        "-c",
        help="Path to configuration file",
        exists=True,
        dir_okay=False,
    ),
    plugins_path: Path = typer.Option(
        None,
        "--plugins-path",
        help="Path to plugins directory",
        file_okay=False,
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose output",
    ),
):
    """
    Global options for all commands.
    """
    if plugins_path is not None:
        import_plugins(plugins_path)

        console.print(
            Panel(
                Pretty(PluginRegistry.representation()),
                title="[bold]Plugin Registry[/bold]",
                border_style="green",
            )
        )

    config = get_config(config_path)

    console.print(
        Panel(
            Pretty(config),
            title="[bold]Loaded Configuration[/bold]",
            subtitle=(
                ":scroll: Using [bold magenta]DEFAULT[/bold magenta] config path"
                if config == DEFAULT_CONFIG
                else f":scroll: [bold yellow]Loaded from[/bold yellow] {config_path!r}"
            ),
            border_style="yellow",
        )
    )

    resources = get_resources(config)

    ctx.obj = AppContext(
        config=config,
        config_path=config_path,
        plugins_path=plugins_path,
        verbose=verbose,
        resources=resources,
    )
