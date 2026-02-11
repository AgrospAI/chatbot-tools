from typing import Annotated

import humanize
import typer

from fastrag import (
    inject,
)
from fastrag.cache.cache import ICache
from fastrag.console import console
from fastrag.context import AppContext

app = typer.Typer()


@app.command()
def clean(
    ctx: typer.Context,
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
    """Clean the cache"""
    if not sure:
        raise typer.Abort()

    ctx: AppContext = ctx.obj

    console.quiet = True

    cache = inject(
        ICache,
        ctx.config.resources.cache.strategy,
        lifespan=ctx.config.resources.cache.lifespan,
    )
    size = cache.clean()

    console.quiet = False

    console.print(f"[bold green] Deleted {humanize.naturalsize(size)}[/bold green]")
