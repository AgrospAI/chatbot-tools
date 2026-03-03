from dataclasses import dataclass, field
from typing import ClassVar, List, override

import uuid6
from sqlalchemy import Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, Session, mapped_column

from fastrag.serve.database import Base, SessionLocal
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
    supported: ClassVar[str] = "parent-chunk-db"

    db: Session | None = field(default=None, repr=False)

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

        if self.db is not None:
            return self._resolve_parent_documents(child_docs, ParentStore(self.db))

        with SessionLocal() as session:
            return self._resolve_parent_documents(child_docs, ParentStore(session))

    def _resolve_parent_documents(
        self,
        child_docs: List[Document],
        parent_store: "ParentStore",
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

            try:
                parent_id = uuid6.UUID(parent_id_str)
                parent_data = parent_store.get_parents(parent_id)

                if parent_data:
                    result_docs.append(
                        Document(
                            page_content=parent_data["content"],
                            metadata=parent_data["doc_metadata"] or {},
                        )
                    )
                else:
                    result_docs.append(child_doc)
            except ValueError:
                result_docs.append(child_doc)

        return result_docs


class ParentStore:
    def __init__(self, db: Session) -> None:
        self.db = db

    def save_parents(self, parent_id: uuid6.UUID, content: str, doc_metadata: dict) -> None:
        chunk = self.db.get(ParentDocuments, parent_id)

        if not chunk:
            chunk = ParentDocuments(
                parent_id=parent_id, content=content, doc_metadata=doc_metadata
            )
            self.db.add(chunk)
        else:
            chunk.content = content
            chunk.doc_metadata = doc_metadata

        self.db.commit()

    def get_parents(self, parent_id: uuid6.UUID):
        chunk = (
            self.db.query(ParentDocuments)
            .filter(ParentDocuments.parent_id == parent_id)
            .first()
        )
        if not chunk:
            return None
        return {
            "parent_id": str(chunk.parent_id),
            "content": chunk.content,
            "doc_metadata": chunk.doc_metadata,
        }
