import asyncio

import typer
from rich.panel import Panel

from fastrag import (
    IRunner,
    inject,
    version,
)
from fastrag.console import console
from fastrag.context import AppContext
from fastrag.steps.logs import Loggable

app = typer.Typer()


@app.command()
def run(
    ctx: typer.Context,
):
    """
    Go through the process of generating a fastRAG.
    """
    ctx: AppContext = ctx.obj

    console.print(
        Panel.fit(
            f"[bold cyan]fastrag[/bold cyan] [green]v{version('fastrag-cli')}[/green]",
            border_style="cyan",
        ),
        justify="center",
    )

    console.quiet = not ctx.verbose
    Loggable.is_verbose = ctx.verbose

    config = ctx.config
    resources = ctx.resources

    async def run():
        async with resources.cache:
            ran = await inject(
                IRunner,
                config.resources.sources.strategy,
                **config.resources.sources.params or {},
            ).run(
                config.resources.sources.steps,
                resources,
            )

            ran = await inject(
                IRunner,
                config.experiments.strategy,
                **config.experiments.params or {},
            ).run(
                config.experiments.steps,
                resources,
                starting_step_number=ran,
            )

            console.print(
                f"[bold green]:heavy_check_mark: Completed {ran} experiments![/bold green]"
            )

    asyncio.run(run())
