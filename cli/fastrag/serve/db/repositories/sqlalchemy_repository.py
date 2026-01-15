from typing import Any, Dict, List, Optional
from uuid import UUID

from fastrag.config.settings import settings
from fastrag.serve.db.database import get_db
from fastrag.serve.db.models import Chat, ChatMessage


class SQLAlchemyChatRepository:
    def get_chat_by_id(self, chat_id: UUID) -> Optional[Dict[str, Any]]:
        _, SessionLocal, _ = get_db(settings)
        if SessionLocal is None:
            raise RuntimeError("Database not configured")
        session = SessionLocal()
        try:
            chat = session.query(Chat).filter(getattr(Chat, "chat_id", None) == chat_id).first()
            if not chat:
                return None
            messages = (
                session.query(ChatMessage)
                .filter(getattr(ChatMessage, "chat_id", None) == chat_id)
                .order_by(getattr(ChatMessage, "created_at", None))
                .all()
            )
            return {
                "chat_id": str(getattr(chat, "chat_id", chat_id)),
                "created_at": getattr(chat, "created_at", None),
                "messages": [
                    {
                        "message_id": getattr(msg, "message_id", None),
                        "chat_id": str(getattr(msg, "chat_id", chat_id)),
                        "role": getattr(msg, "role", None),
                        "content": getattr(msg, "content", None),
                        "created_at": getattr(msg, "created_at", None),
                        "sources": getattr(msg, "sources", None),
                    }
                    for msg in messages
                ],
            }
        finally:
            session.close()

    def save_message(
        self,
        chat_id: UUID,
        content: str,
        role: str,
        sources: Optional[List[str]] = None,
    ) -> None:
        _, SessionLocal, _ = get_db(settings)
        if SessionLocal is None:
            raise RuntimeError("Database not configured")
        session = SessionLocal()
        try:
            chat = session.query(Chat).filter(getattr(Chat, "chat_id", None) == chat_id).first()
            if not chat:
                chat = Chat()
                if hasattr(chat, "chat_id"):
                    chat.chat_id = chat_id
                session.add(chat)
                session.flush()
            chat_msg = ChatMessage()
            if hasattr(chat_msg, "chat_id"):
                chat_msg.chat_id = chat_id
            if hasattr(chat_msg, "content"):
                chat_msg.content = content
            if hasattr(chat_msg, "role"):
                chat_msg.role = role
            if hasattr(chat_msg, "sources"):
                chat_msg.sources = sources
            session.add(chat_msg)
            session.commit()
        finally:
            session.close()

    def get_chats(
        self,
        page: int = 1,
        page_size: int = 10,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> Dict[str, Any]:
        _, SessionLocal, _ = get_db(settings)
        if SessionLocal is None:
            raise RuntimeError("Database not configured")
        session = SessionLocal()
        try:
            query = session.query(Chat)
            sort_column = getattr(Chat, sort_by, getattr(Chat, "created_at", None))
            if sort_order == "desc" and hasattr(sort_column, "desc"):
                query = query.order_by(sort_column.desc())
            elif hasattr(sort_column, "asc"):
                query = query.order_by(sort_column.asc())
            total_count = query.count()
            offset = (page - 1) * page_size
            chats = query.offset(offset).limit(page_size).all()
            return {
                "items": [
                    {
                        "chat_id": str(getattr(chat, "chat_id", None)),
                        "created_at": getattr(chat, "created_at", None),
                    }
                    for chat in chats
                ],
                "total": total_count,
                "page": page,
                "page_size": page_size,
                "total_pages": (total_count + page_size - 1) // page_size,
            }
        finally:
            session.close()
