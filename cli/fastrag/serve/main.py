import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded

from fastrag import ILLM, Config
from fastrag.config.env import load_env_file
from fastrag.config.loaders.loader import IConfigLoader
from fastrag.embeddings import IEmbeddings
from fastrag.plugins import import_plugins, inject
from fastrag.serve.rate_limiter import custom_rate_limit_handler, limiter
from fastrag.settings import DEFAULT_CONFIG
from fastrag.stores.store import IVectorStore

from .dependencies import set_dependencies
from .endpoints.ask import router as ask_router
from .endpoints.chats import router as chats_router
from .endpoints.healthz import router as health_router
from .endpoints.metrics import router as metrics_router

vector_store = None
llm = None
config = None
embedding_model = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    if vector_store is None or llm is None:
        raise RuntimeError(
            "Server not initialized. Call init_serve(config) before starting the app."
        )
    yield


def init_serve(app_config: Config) -> None:
    global config, vector_store, llm, embedding_model
    config = app_config
    if config.resources.store is None:
        raise ValueError("Vector store configuration is required for serve command")
    if config.resources.llm is None:
        raise ValueError("LLM configuration is required for serve command")
    if "embedding" not in config.experiments.steps.keys():
        raise ValueError("Embedding configuration is required for vector store")
    embedding_config = config.experiments.steps["embedding"][0]
    embedding_model = inject(IEmbeddings, embedding_config.strategy, **embedding_config.params)
    vector_store = inject(
        IVectorStore,
        config.resources.store.strategy,
        embedding_model=embedding_model,
        **config.resources.store.params,
    )
    llm = inject(ILLM, config.resources.llm.strategy, **config.resources.llm.params)
    set_dependencies(config, vector_store, llm, embedding_model)


def _make_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)
    app.state.limiter = limiter

    app.add_exception_handler(RateLimitExceeded, custom_rate_limit_handler)

    origins = ["*"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router)
    app.include_router(metrics_router)
    app.include_router(ask_router)
    app.include_router(chats_router)
    return app


def create_app() -> FastAPI:
    load_env_file()
    plugins_dir = os.environ.get("FASTRAG_PLUGINS_DIR")
    if plugins_dir:
        import_plugins(Path(plugins_dir))
    cfg_path_str = os.environ.get("FASTRAG_CONFIG_PATH")
    cfg_path = Path(cfg_path_str) if cfg_path_str else DEFAULT_CONFIG
    loader = inject(IConfigLoader, cfg_path.suffix)
    cfg: Config = loader.load(cfg_path)
    init_serve(cfg)
    app = _make_app()
    return app


def start_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    if reload:
        import uvicorn

        uvicorn.run(
            "fastrag.serve.main:create_app",
            host=host,
            port=port,
            reload=True,
            factory=True,
        )
    else:
        import uvicorn

        uvicorn.run(
            create_app(),
            host=host,
            reload=False,
        )


if __name__ == "__main__":
    start_server(reload=True)
