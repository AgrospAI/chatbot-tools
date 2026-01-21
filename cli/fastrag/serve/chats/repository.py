from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi import Depends
from sqlalchemy.orm import Session

from fastrag.serve.chats.model import Chat, ChatMessage
from fastrag.serve.database import get_db


class ChatRepository:
    db: Session

    def __init__(self, db: Session = Depends(get_db)) -> None:
        self.db = db

    def get_chat_by_id(self, chat_id: UUID) -> Optional[Dict[str, Any]]:
        chat = self.db.query(Chat).filter(getattr(Chat, "chat_id", None) == chat_id).first()
        if not chat:
            return None

        messages = (
            self.db.query(ChatMessage)
            .filter(getattr(ChatMessage, "chat_id", None) == chat_id)
            .order_by(getattr(ChatMessage, "created_at", None))
            .all()
        )

        return {
            "chat_id": str(getattr(chat, "chat_id", chat_id)),
            "created_at": getattr(chat, "created_at", None),
            "ip": getattr(chat, "ip", None),
            "country": getattr(chat, "country", None),
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

    def save_message(
        self,
        chat_id: UUID,
        content: str,
        role: str,
        sources: Optional[List[str]] = None,
        ip: Optional[str] = None,
        country: Optional[str] = None,
    ) -> None:
        chat = self.db.query(Chat).filter(getattr(Chat, "chat_id", None) == chat_id).first()
        if not chat:
            chat = Chat()
            if hasattr(chat, "chat_id"):
                chat.chat_id = chat_id
            if hasattr(chat, "ip"):
                chat.ip = ip
            if hasattr(chat, "country"):
                chat.country = country
            self.db.add(chat)
            self.db.flush()
        chat_msg = ChatMessage()
        if hasattr(chat_msg, "chat_id"):
            chat_msg.chat_id = chat_id
        if hasattr(chat_msg, "content"):
            chat_msg.content = content
        if hasattr(chat_msg, "role"):
            chat_msg.role = role
        if hasattr(chat_msg, "sources"):
            chat_msg.sources = sources
        self.db.add(chat_msg)
        self.db.commit()

    def get_chats(
        self,
        page: int = 1,
        page_size: int = 10,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> Dict[str, Any]:
        query = self.db.query(Chat)
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
                    "ip": getattr(chat, "ip", None),
                    "country": getattr(chat, "country", None),
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


def get_chat_repository(db: Session = Depends(get_db)) -> ChatRepository:
    return ChatRepository(db)
