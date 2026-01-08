import os
import shutil
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel
from rich.pretty import Pretty

from fastrag import (
    Config,
    Constants,
    init_constants,
    version,
)
from fastrag.config.env import load_env_file
from fastrag.plugins import PluginRegistry, import_path
from fastrag.settings import DEFAULT_CONFIG
from fastrag.systems import System

app = typer.Typer(help="CLI RAG generator", add_completion=False)
console = Console()


@app.command()
def serve(
    config: Annotated[
        Path,
        typer.Argument(help="Path to the config file."),
    ] = DEFAULT_CONFIG,
    plugins: Annotated[
        Path | None,
        typer.Option("--plugins", "-p", help="Path to the plugins directory."),
    ] = None,
    host: Annotated[
        str,
        typer.Option("--host", "-h", help="Host to bind the server to."),
    ] = "0.0.0.0",
    port: Annotated[
        int,
        typer.Option("--port", help="Port to bind the server to."),
    ] = 8000,
    reload: Annotated[
        bool,
        typer.Option("--reload", "-r", help="Enable auto-reload for development."),
    ] = False,
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Verbose prints"),
    ] = False,
):
    """
    Start the FastRAG API server for question answering.
    """
    console.print(
        Panel.fit(
            f"[bold cyan]fastrag serve[/bold cyan] [green]v{version('fastrag')}[/green]",
            border_style="cyan",
        ),
        justify="center",
    )

    console.quiet = not verbose

    # Load plugins before config
    load_plugins(plugins)

    # Load configuration
    cfg = load_config(config, verbose)

    # Import and initialize serve module
    from fastrag.serve import init_serve, start_server

    # Initialize the server with config
    init_serve(cfg)

    # Start the server
    # Provide paths via env vars so reload subprocess can re-init correctly
    os.environ["FASTRAG_CONFIG_PATH"] = str(config.resolve())
    if plugins is not None:
        os.environ["FASTRAG_PLUGINS_DIR"] = str(plugins.resolve())

    start_server(host=host, port=port, reload=reload)


@app.command()
def clean(
    sure: Annotated[
        bool,
        typer.Option(
            "--yes",
            "-y",
            prompt="Are you sure you want to continue?",
            confirmation_prompt=True,
        ),
    ] = False,
):
    """Clean the caches"""

    if not sure:
        raise typer.Abort()

    path = Constants.global_cache()
    if not path.exists():
        console.print(f"[bold red]Could not find global cache at {path}[/bold red]")
        raise typer.Abort()

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
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Verbose prints"),
    ] = False,
):
    """
    Go through the process of generating a fastRAG.
    """

    console.print(
        Panel.fit(
            f"[bold cyan]fastrag[/bold cyan] [green]v{version('fastrag')}[/green]",
            border_style="cyan",
        ),
        justify="center",
    )

    console.quiet = not verbose

    # Load plugins before config
    load_plugins(plugins)
    PluginRegistry.get_instance(System.RUNNER, "async").run(load_config(config, verbose), step)


def load_config(path: Path, verbose: bool) -> Config:
    # Load environment variables from .env file before loading config
    load_env_file()

    config = PluginRegistry.get_instance(System.CONFIG_LOADER, path.suffix).load(path)
    init_constants(config, verbose)
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
    if plugins is not None:
        import_path(plugins)

    console.print(
        Panel(
            Pretty(PluginRegistry.representation()),
            title="[bold]Plugin Registry[/bold]",
            border_style="green",
        )
    )


if __name__ == "__main__":
    app()
