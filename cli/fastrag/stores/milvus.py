from dataclasses import dataclass
from typing import List, override

from fastrag.embeddings import IEmbeddings
from fastrag.plugins import plugin
from fastrag.stores.store import Document, IVectorStore
from fastrag.systems import System


@dataclass
@plugin(system=System.VECTOR_STORE, supported="milvus")
class MilvusVectorStore(IVectorStore):
    """Milvus vector store implementation"""

    host: str
    port: int
    collection_name: str
    user: str | None = None
    password: str | None = None
    embedding_model: IEmbeddings | None = None

    def __post_init__(self):
        """Initialize Milvus connection lazily"""
        self._store = None

    def _get_store(self):
        """Lazy initialization of Milvus connection"""
        if self._store is None:
            try:
                from langchain_milvus.vectorstores import Milvus
            except ImportError:
                raise ImportError(
                    "langchain-milvus is required for Milvus support. "
                    "Install it with: pip install langchain-milvus"
                )

            connection_args = {
                "uri": f"tcp://{self.host}:{self.port}",
            }

            if self.user and self.password:
                connection_args["token"] = f"{self.user}:{self.password}"

            # Create a wrapper for the embedding model
            from langchain_core.embeddings import Embeddings as LCEmbeddings

            class EmbeddingWrapper(LCEmbeddings):
                def __init__(self, embedding_model: IEmbeddings):
                    self.embedding_model = embedding_model

                def embed_documents(self, texts: List[str]) -> List[List[float]]:
                    return self.embedding_model.embed_documents(texts)

                def embed_query(self, text: str) -> List[float]:
                    return self.embedding_model.embed_query(text)

            embedding_function = EmbeddingWrapper(self.embedding_model)

            self._store = Milvus(
                embedding_function=embedding_function,
                collection_name=self.collection_name,
                connection_args=connection_args,
            )

        return self._store

    @override
    async def add_documents(
        self, documents: List[Document], embeddings: List[List[float]]
    ) -> List[str]:
        """Add documents with their embeddings to Milvus"""
        store = self._get_store()

        # Convert to langchain documents
        from langchain_core.documents import Document as LCDocument

        lc_docs = [
            LCDocument(page_content=doc.page_content, metadata=doc.metadata)
            for doc in documents
        ]

        # Add documents (Milvus will use the embedding function to embed them)
        ids = await store.aadd_documents(lc_docs)
        return ids

    @override
    async def similarity_search(
        self, query: str, query_embedding: List[float], k: int = 5
    ) -> List[Document]:
        """Search for similar documents in Milvus"""
        store = self._get_store()

        # Use the query text - Milvus will embed it using the embedding function
        results = await store.asimilarity_search(query=query, k=k)

        # Convert back to our Document format
        return [
            Document(page_content=doc.page_content, metadata=doc.metadata) for doc in results
        ]

    @override
    async def delete_collection(self) -> None:
        """Delete the Milvus collection"""
        store = self._get_store()
        await store.adelete_collection()

    @override
    async def collection_exists(self) -> bool:
        """Check if the Milvus collection exists"""
        store = self._get_store()
        # Milvus auto-creates collections, so we can check if it has documents
        try:
            await store.asimilarity_search("test", k=1)
            return True
        except Exception:
            return False
