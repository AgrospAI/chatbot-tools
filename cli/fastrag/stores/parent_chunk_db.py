from dataclasses import dataclass, field
from typing import ClassVar, List, override

import uuid6
from sqlalchemy import Text, select
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.selectable import Select

from fastrag.serve.database import Base, initialize_database, session_context
from fastrag.stores.milvus import MilvusVectorStore
from fastrag.stores.store import Document


class ParentDocuments(Base):
    __tablename__ = "parent_documents"

    parent_id: Mapped[uuid6.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid6.uuid7
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    doc_metadata: Mapped[dict] = mapped_column(JSONB)


@dataclass
class ParentVectorStore(MilvusVectorStore):
    supported: ClassVar[str] = "parent-child-milvus"

    store: "ParentStore" = field(init=False)

    def __post_init__(self) -> None:
        self.store = ParentStore()

    @override
    async def similarity_search(
        self,
        query: str,
        query_embedding: List[float],
        k: int = 5,
        collection_name: str | None = None,
    ) -> List[Document]:
        child_docs = await super().similarity_search(
            query=query,
            query_embedding=query_embedding,
            k=k,
            collection_name=collection_name,
        )

        return await self._resolve_parent_documents(child_docs)

    async def _resolve_parent_documents(
        self,
        child_docs: List[Document],
    ) -> List[Document]:
        result_docs = []
        seen_parent_ids = set()

        for child_doc in child_docs:
            parent_id_str = child_doc.metadata.get("parent_id")

            if not parent_id_str:
                result_docs.append(child_doc)
                continue

            if parent_id_str in seen_parent_ids:
                continue

            seen_parent_ids.add(parent_id_str)

            parent_id = uuid6.UUID(parent_id_str)
            parent_data = await self.store.get_parents(parent_id)

            if parent_data:
                result_docs.append(
                    Document(
                        chunk_id=child_doc.chunk_id,
                        page_content=parent_data["content"],
                        metadata=parent_data["doc_metadata"] or {},
                        parent_id=str(parent_id),
                    )
                )
            else:
                result_docs.append(child_doc)
            result_docs.append(child_doc)

        return result_docs


@dataclass
class ParentStore:
    async def save_parents(
        self,
        parent_id: uuid6.UUID,
        content: str,
        doc_metadata: dict,
    ) -> None:
        await initialize_database()
        async with session_context() as db:
            chunk = await db.get(ParentDocuments, parent_id)

            if not chunk:
                chunk = ParentDocuments(
                    parent_id=parent_id, content=content, doc_metadata=doc_metadata
                )
                db.add(chunk)
            else:
                chunk.content = content
                chunk.doc_metadata = doc_metadata

            await db.commit()

    async def get_parents(
        self,
        parent_id: uuid6.UUID,
    ):
        await initialize_database()
        async with session_context() as db:
            query: Select[tuple[ParentDocuments]] = select(ParentDocuments).filter(
                ParentDocuments.parent_id == parent_id
            )
            result = await db.execute(query)
            chunk = result.scalars().first()

            if not chunk:
                return None

            return {
                "parent_id": str(chunk.parent_id),
                "content": chunk.content,
                "doc_metadata": chunk.doc_metadata,
            }
