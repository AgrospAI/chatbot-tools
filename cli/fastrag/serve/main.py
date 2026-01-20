import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.embeddings import Embeddings
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from prometheus_client import make_asgi_app
from slowapi.errors import RateLimitExceeded

from fastrag import ILLM
from fastrag.serve.ask.route import AskRouter
from fastrag.serve.chats.route import ChatRouter
from fastrag.serve.database import initialize_database
from fastrag.serve.healthz.route import HealthRouter
from fastrag.serve.rate_limiting import custom_rate_limit_handler, limiter
from fastrag.stores.store import IVectorStore


def create_app(embedding_model: Embeddings, vector_store: IVectorStore, llm: ILLM) -> FastAPI:
    initialize_database()

    app = FastAPI()

    app.state.limiter = limiter
    app.state.embedding_model = embedding_model
    app.state.vector_store = vector_store
    app.state.llm = llm

    app.add_exception_handler(RateLimitExceeded, custom_rate_limit_handler)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(HealthRouter)
    app.include_router(AskRouter)
    app.include_router(ChatRouter)

    FastAPIInstrumentor.instrument_app(app)

    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)

    return app


def start_server(
    host: str = "0.0.0.0",
    port: int = 8000,
    reload: bool = False,
    embedding_model: Embeddings = None,
    vector_store: IVectorStore = None,
    llm: ILLM = None,
):
    if reload:
        uvicorn.run(
            "fastrag.serve.main:create_app", host=host, port=port, reload=True, factory=True
        )
    else:
        app = create_app(
            embedding_model=embedding_model,
            vector_store=vector_store,
            llm=llm,
        )
        uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    start_server(reload=True)
