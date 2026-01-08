import os

os.environ["GRPC_DNS_RESOLVER"] = "native"

import json
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from fastrag import ILLM, Config, init_constants
from fastrag.config.env import load_env_file
from fastrag.plugins import PluginRegistry, import_path
from fastrag.settings import DEFAULT_CONFIG
from fastrag.stores.store import IVectorStore
from fastrag.systems import System

# Global references to configured components
vector_store: IVectorStore = None
llm: ILLM = None
config: Config = None


def init_serve(app_config: Config) -> None:
    """Initialize the serve module with configuration"""
    global config, vector_store, llm

    config = app_config

    if config.vectorstore is None:
        raise ValueError("Vector store configuration is required for serve command")

    if config.llm is None:
        raise ValueError("LLM configuration is required for serve command")

    # Get the embedding model instance
    if not config.steps.embedding:
        raise ValueError("Embedding configuration is required for vector store")

    embedding_config = config.steps.embedding[0]
    embedding_model = PluginRegistry.get_instance(
        System.EMBEDDING, embedding_config.strategy, **embedding_config.params
    )

    # Initialize vector store with embedding model
    vector_store = PluginRegistry.get_instance(
        System.VECTOR_STORE,
        config.vectorstore.strategy,
        embedding_model=embedding_model,
        **config.vectorstore.params,
    )

    # Initialize LLM
    llm = PluginRegistry.get_instance(System.LLM, config.llm.strategy, **config.llm.params)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan context manager"""
    # Components are initialized via init_serve() before app starts
    if vector_store is None or llm is None:
        raise RuntimeError(
            "Server not initialized. Call init_serve(config) before starting the app."
        )
    yield


def _make_app() -> FastAPI:
    app = FastAPI(lifespan=lifespan)

    origins = ["*"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app


class QuestionRequest(BaseModel):
    question: str


def build_prompt(context: str, question: str) -> str:
    """
    Construye el prompt RAG para el LLM.
    """
    return f"""
    You are a helpful assistant and expert in data spaces.

    Always use inline references in the form [<NUMBER OF DOCUMENT>](ref:<NUMBER OF DOCUMENT>)
    ONLY if you use information from a document. For example, if you use the information from
    Document[3], you should write [3](ref:3) at the end of the sentence where you used that
    information.
    Give a precise, accurate and structured answer without repeating the question.
    
    These are the documents:
    {context}

    Question:
    {question}

    Answer:
    """.strip()


def create_app() -> FastAPI:
    """Factory to create and initialize the FastAPI app.

    Supports uvicorn reload by loading configuration on each import, using
    environment variables set by the CLI:
      - FASTRAG_CONFIG_PATH: path to the config file
      - FASTRAG_PLUGINS_DIR: optional path to plugins directory
    """
    # Load env before reading config
    load_env_file()

    # Load plugins (optional)
    plugins_dir = os.environ.get("FASTRAG_PLUGINS_DIR")
    if plugins_dir:
        import_path(Path(plugins_dir))

    # Resolve config path
    cfg_path_str = os.environ.get("FASTRAG_CONFIG_PATH")
    cfg_path = Path(cfg_path_str) if cfg_path_str else DEFAULT_CONFIG

    # Load configuration via registry loader
    loader = PluginRegistry.get_instance(System.CONFIG_LOADER, cfg_path.suffix)
    cfg: Config = loader.load(cfg_path)

    # Initialize constants and serve components
    init_constants(cfg, False)
    init_serve(cfg)

    app = _make_app()

    @app.post("/ask")
    async def ask_question(req: QuestionRequest) -> StreamingResponse:  # type: ignore
        print(f"Received question: {req.question}")

        # Get the embedding for the query
        embedding_config = config.steps.embedding[0]
        embedding_model = PluginRegistry.get_instance(
            System.EMBEDDING, embedding_config.strategy, **embedding_config.params
        )

        query_embedding = embedding_model.embed_query(req.question)

        # Search for similar documents
        results = await vector_store.similarity_search(
            query=req.question, query_embedding=query_embedding, k=5
        )

        context_parts = [f"Document[{i}]: {doc.page_content}" for i, doc in enumerate(results)]
        context = "\n\n".join(context_parts)

        sources_metadata = [doc.metadata.get("source") for doc in results]

        async def generate():
            yield f"data: {json.dumps({'type': 'sources', 'data': sources_metadata})}\n\n"

            prompt = build_prompt(context, req.question)
            async for token in llm.stream(prompt):
                yield f"data: {json.dumps({'type': 'token', 'data': token})}\n\n"

        return StreamingResponse(
            content=generate(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    return app


def start_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """Start the FastAPI server.

    - When reload is False, run with a pre-initialized app object.
    - When reload is True, run using the factory import path so each reload
      properly (re)initializes the app from the config path env var.
    """
    if reload:
        uvicorn.run(
            "fastrag.serve:create_app",
            host=host,
            port=port,
            reload=True,
            factory=True,
        )
    else:
        uvicorn.run(
            create_app(),
            host=host,
            port=port,
            reload=False,
        )


if __name__ == "__main__":
    # Development entry: respect FASTRAG_CONFIG_PATH if set
    start_server(reload=True)
