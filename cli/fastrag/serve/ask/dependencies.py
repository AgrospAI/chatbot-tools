from fastapi import Request


def get_embedding_model(request: Request):
    return request.app.state.embedding_model


def get_vector_store(request: Request):
    return request.app.state.vector_store


def get_llm(request: Request):
    return request.app.state.llm
