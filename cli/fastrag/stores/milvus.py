import os
from dataclasses import dataclass, field
from typing import ClassVar, List, override

os.environ["GRPC_VERBOSITY"] = "ERROR"
os.environ["GRPC_DNS_RESOLVER"] = "native"
from pymilvus import AsyncMilvusClient, DataType

from fastrag.embeddings import IEmbeddings
from fastrag.stores.store import Document, IVectorStore


@dataclass
class MilvusVectorStore(IVectorStore):
    """Milvus vector store implementation using Async Milvus Client"""

    supported: ClassVar[str] = "milvus"

    host: str
    port: int
    collection_name: str
    user: str | None = None
    password: str | None = None
    embedding_model: IEmbeddings | None = None
    dimension: int = 768

    # Internal state
    _client: any = field(default=None, repr=False, init=False)

    async def _get_client(self, collection_name: str | None = None) -> AsyncMilvusClient:
        """Initialize the true Async Milvus Client"""
        if self._client is None:
            # MilvusClientAsync expects a uri string
            uri = f"http://{self.host}:{self.port}"
            token = f"{self.user}:{self.password}" if self.user else ""

            client = AsyncMilvusClient(uri=uri, token=token)
            await self._ensure_collection(client, collection_name)

            self._client = client
        return self._client

    async def _ensure_collection(
        self,
        client: AsyncMilvusClient,
        collection_name: str | None = None,
    ):
        """Creates collection matching the docs_chatbot schema exactly."""
        collection_name = self._get_collection(collection_name)

        exists = await client.has_collection(collection_name)
        if not exists:
            schema = client.create_schema(
                auto_id=True,  # Matches autoID: true in your schema
                enable_dynamic_field=False,  # Your schema shows dynamicFields: []
            )

            # 2. Add Fields exactly as defined in your JSON
            # Field 101: pk (Primary Key)
            schema.add_field(field_name="pk", datatype=DataType.INT64, is_primary=True)

            # Field 100: text
            schema.add_field(field_name="text", datatype=DataType.VARCHAR, max_length=65535)

            # Field 102: vector
            schema.add_field(
                field_name="vector", datatype=DataType.FLOAT_VECTOR, dim=self.dimension
            )

            # Field 103: source
            schema.add_field(field_name="metadata", datatype=DataType.JSON)

            # 3. Setup Index Parameters using AUTOINDEX and L2 metric
            index_params = client.prepare_index_params()
            index_params.add_index(
                field_name="vector",
                index_name="vector",
                index_type="AUTOINDEX",
                metric_type="L2",
            )

            # 4. Create and Load
            await client.create_collection(
                collection_name=collection_name,
                schema=schema,
                index_params=index_params,
            )
            await client.load_collection(collection_name)

    @override
    async def add_documents(
        self,
        documents: List[Document],
        embeddings: List[List[float]],
        collection_name: str | None = None,
    ) -> List[str]:
        collection_name = self._get_collection(collection_name)
        client = await self._get_client(collection_name)

        # Data mapping for Milvus
        data = [
            {"vector": embeddings[i], "text": doc.page_content, "metadata": doc.metadata}
            for i, doc in enumerate(documents)
        ]

        res = await client.insert(collection_name=collection_name, data=data)
        return [str(i) for i in res.get("ids", [])]

    @override
    async def similarity_search(
        self,
        query: str,
        query_embedding: List[float],
        k: int = 5,
        collection_name: str | None = None,
    ) -> List[Document]:
        collection_name = self._get_collection(collection_name)

        client = await self._get_client(collection_name)

        res = await client.search(
            collection_name=collection_name,
            anns_field="vector",
            data=[query_embedding],
            search_params={"metric_type": "L2", "params": {}},
            limit=k,
            output_fields=["text", "metadata"],
        )

        docs = []
        if res and len(res) > 0:
            for hit in res[0]:
                entity = hit.get("entity", {})
                docs.append(
                    Document(
                        page_content=entity.get("text", ""), metadata=entity.get("metadata", {})
                    )
                )
        return docs

    @override
    async def collection_exists(self, collection_name: str | None = None) -> bool:
        collection_name = self._get_collection(collection_name)

        client = await self._get_client(collection_name)
        return await client.has_collection(collection_name)

    @override
    async def delete_collection(self, collection_name: str | None = None) -> None:
        """Required implementation: Drops the collection from Milvus"""
        collection_name = self._get_collection(collection_name)

        client = await self._get_client(collection_name)
        if await client.has_collection(collection_name):
            await client.drop_collection(collection_name)

    @override
    async def embed_query(self, text: str) -> List[float]:
        """Required implementation: Delegates to the assigned embedding model"""
        return await self.embedding_model.embed_query(text)

    def _get_collection(self, collection_name: str | None) -> str:
        return collection_name if collection_name else self.collection_name
