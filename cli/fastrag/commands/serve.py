from typing import Annotated

import typer
from langchain_core.embeddings import Embeddings
from rich.panel import Panel

from fastrag import (
    version,
)
from fastrag.console import console
from fastrag.context import AppContext
from fastrag.llms.llm import ILLM
from fastrag.plugins import inject
from fastrag.steps.logs import Loggable
from fastrag.stores.store import IVectorStore

app = typer.Typer()


@app.command()
def serve(
    ctx: typer.Context,
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
):
    """
    Start the FastRAG API server for question answering.
    """
    ctx: AppContext = ctx.obj

    console.print(
        Panel.fit(
            f"[bold cyan]fastrag serve[/bold cyan] [green]v{version('fastrag-cli')}[/green]",
            border_style="cyan",
        ),
        justify="center",
    )

    console.quiet = not ctx.verbose
    Loggable.is_verbose = ctx.verbose

    config = ctx.config

    if config.resources.store is None:
        raise ValueError("Vector store configuration is required for serve command")
    if config.resources.llm is None:
        raise ValueError("LLM configuration is required for serve command")
    if "embedding" not in config.experiments.steps.keys():
        raise ValueError("Embedding configuration is required for vector store")

    embedding_config = config.experiments.steps["embedding"][0]
    embedding_model = inject(Embeddings, embedding_config.strategy, **embedding_config.params)
    vector_store = inject(
        IVectorStore,
        config.resources.store.strategy,
        embedding_model=embedding_model,
        **config.resources.store.params,
    )
    llm = inject(ILLM, config.resources.llm.strategy, **config.resources.llm.params)

    from fastrag.serve.main import start_server

    start_server(
        host=host,
        port=port,
        reload=reload,
        embedding_model=embedding_model,
        vector_store=vector_store,
        llm=llm,
    )
