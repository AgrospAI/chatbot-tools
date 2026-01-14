from typing import Any, Dict, List
from uuid import uuid4

from fastrag.serve.db.database import SessionLocal
from fastrag.serve.db.models import ChatMessage


class ChatRepositoryBase:
    def save_message(
        self, chat_id: str, message: str, role: str, meta: Dict[str, Any] = None
    ) -> None:
        raise NotImplementedError

    def get_messages(self, chat_id: str) -> List[Dict[str, Any]]:
        raise NotImplementedError


class SQLAlchemyChatRepository(ChatRepositoryBase):
    def save_message(
        self, chat_id: str, message: str, role: str, meta: Dict[str, Any] = None
    ) -> None:
        session = SessionLocal()
        try:
            chat_msg = ChatMessage(
                id=str(uuid4()),
                chat_id=chat_id,
                message=message,
                role=role,
                meta=str(meta) if meta else None,
            )
            session.add(chat_msg)
            session.commit()
        finally:
            session.close()

    def get_messages(self, chat_id: str) -> List[Dict[str, Any]]:
        session = SessionLocal()
        try:
            msgs = session.query(ChatMessage).filter(ChatMessage.chat_id == chat_id).all()
            return [
                {
                    "id": msg.id,
                    "chat_id": msg.chat_id,
                    "message": msg.message,
                    "role": msg.role,
                    "meta": msg.meta,
                    "created_at": msg.created_at,
                }
                for msg in msgs
            ]
        finally:
            session.close()
