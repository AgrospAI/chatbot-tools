import asyncio

import uvicorn
from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.embeddings import Embeddings
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from prometheus_client import make_asgi_app
from slowapi.errors import RateLimitExceeded

from fastrag import ILLM
from fastrag.logging import logger
from fastrag.serve.ask.route import router as ask_router
from fastrag.serve.chats.route import router as chat_router
from fastrag.serve.database import Base, engine
from fastrag.serve.geolocalization.middleware import GeoIPMiddleware
from fastrag.serve.healthz.route import router as health_router
from fastrag.serve.rate_limiting import custom_rate_limit_handler, limiter
from fastrag.serve.telemetry.middleware import MetricsMiddleware
from fastrag.stores.store import IVectorStore


@asynccontextmanager
async def lifespan(_: FastAPI):
    # Wait database
    while True:
        try:
            async with engine.connect():
                logger.info("Successfully connected to the database.")
                break
        except KeyboardInterrupt:
            exit(-1)
        except Exception as e:
            logger.exception(e)
            logger.info("Database not reachable, waiting %d seconds...", 5)
            await asyncio.sleep(5)

    # Initialize the database
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    yield


def create_app(
    embedding_model: Embeddings | None,
    vector_store: IVectorStore | None,
    llm: ILLM | None,
) -> FastAPI:
    app = FastAPI(lifespan=lifespan)

    app.state.limiter = limiter
    app.state.embedding_model = embedding_model
    app.state.vector_store = vector_store
    app.state.llm = llm

    app.add_exception_handler(RateLimitExceeded, custom_rate_limit_handler)

    app.add_middleware(
        MetricsMiddleware,  # type: ignore
    )
    app.add_middleware(
        GeoIPMiddleware,  # type: ignore
    )
    app.add_middleware(
        CORSMiddleware,  # type: ignore
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router)
    app.include_router(ask_router)
    app.include_router(chat_router)

    FastAPIInstrumentor.instrument_app(app)

    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)

    return app


def start_server(
    host: str = "0.0.0.0",
    port: int = 8000,
    reload: bool = False,
    embedding_model: Embeddings | None = None,
    vector_store: IVectorStore | None = None,
    llm: ILLM | None = None,
):
    app = create_app(
        embedding_model=embedding_model,
        vector_store=vector_store,
        llm=llm,
    )

    uvicorn.run(app, host=host, port=port, reload=reload)


if __name__ == "__main__":
    start_server(reload=True)
