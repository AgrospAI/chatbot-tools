import os
from pathlib import Path
from typing import Annotated

import humanize
import typer
from rich.console import Console
from rich.panel import Panel
from rich.pretty import Pretty

from fastrag import (
    DEFAULT_CONFIG,
    Config,
    IConfigLoader,
    IRunner,
    PluginRegistry,
    import_plugins,
    inject,
    load_env_file,
    version,
)
from fastrag.cache.cache import ICache
from fastrag.steps.logs import Loggable

app = typer.Typer(help="FastRAG CLI", add_completion=False)
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
            f"[bold cyan]fastrag serve[/bold cyan] [green]v{version('fastrag-cli')}[/green]",
            border_style="cyan",
        ),
        justify="center",
    )

    console.quiet = not verbose
    Loggable.is_verbose = verbose

    # Load plugins before config
    load_plugins(plugins)

    # Load configuration
    cfg = load_config(config)

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
    config: Annotated[
        Path,
        typer.Argument(help="Path to the config file."),
    ] = DEFAULT_CONFIG,
    plugins: Annotated[
        Path | None,
        typer.Option("--plugins", "-p", help="Path to the plugins directory."),
    ] = None,
):
    """Clean the cache"""

    if not sure:
        raise typer.Abort()

    # Load plugins before config
    load_plugins(plugins)
    config: Config = load_config(config)

    cache = inject(
        ICache, config.resources.cache.strategy, lifespan=config.resources.cache.lifespan
    )
    size = cache.clean()

    console.print(f"[bold green] Deleted {humanize.naturalsize(size)}[/bold green]")


@app.command()
def run(
    config: Annotated[
        Path,
        typer.Argument(help="Path to the config file."),
    ] = DEFAULT_CONFIG,
    step: Annotated[
        int,
        typer.Option(
            "--step",
            "-s",
            help="What step to execute up to",
        ),
    ] = -1,
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
            f"[bold cyan]fastrag[/bold cyan] [green]v{version('fastrag-cli')}[/green]",
            border_style="cyan",
        ),
        justify="center",
    )

    console.quiet = not verbose
    Loggable.is_verbose = verbose

    # Load plugins before config
    load_plugins(plugins)
    config: Config = load_config(config)
    cache = inject(
        ICache,
        config.resources.cache.strategy,
        lifespan=config.resources.cache.lifespan,
    )

    ran = inject(IRunner, config.resources.sources.strategy).run(
        config.resources.sources.steps,
        cache,
        step,
    )
    ran += inject(IRunner, config.experiments.strategy).run(
        config.experiments.steps,
        cache,
        step,
        starting_step_number=ran,
    )

    console.print(f"[bold green]:heavy_check_mark: Completed {ran} steps![/bold green]")


def load_config(path: Path) -> Config:
    # Load environment variables from .env file before loading config
    load_env_file()

    config = inject(IConfigLoader, path.suffix).load(path)
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
        import_plugins(plugins)

    console.print(
        Panel(
            Pretty(PluginRegistry.representation()),
            title="[bold]Plugin Registry[/bold]",
            border_style="green",
        )
    )
