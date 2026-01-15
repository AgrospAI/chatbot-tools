from typing import Any, Dict, List, Optional
from uuid import UUID

from fastrag.serve.db.database import SessionLocal
from fastrag.serve.db.models import Chat, ChatMessage


class SQLAlchemyChatRepository:
    def get_chat_by_id(self, chat_id: UUID) -> Optional[Dict[str, Any]]:
        session = SessionLocal()
        try:
            chat = session.query(Chat).filter(Chat.chat_id == chat_id).first()
            if not chat:
                return None
            messages = (
                session.query(ChatMessage)
                .filter(ChatMessage.chat_id == chat_id)
                .order_by(ChatMessage.created_at)
                .all()
            )
            return {
                "chat_id": str(chat.chat_id),
                "created_at": chat.created_at,
                "messages": [
                    {
                        "message_id": msg.message_id,
                        "chat_id": str(msg.chat_id),
                        "role": msg.role,
                        "content": msg.content,
                        "created_at": msg.created_at,
                        "sources": msg.sources,
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
        session = SessionLocal()
        try:
            # Ensure chat exists
            chat = session.query(Chat).filter(Chat.chat_id == chat_id).first()
            if not chat:
                chat = Chat(chat_id=chat_id)
                session.add(chat)
                session.flush()  # Assign PK
            chat_msg = ChatMessage(
                chat_id=chat_id,
                content=content,
                role=role,
                sources=sources,
            )
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
        session = SessionLocal()
        try:
            # Build base query
            query = session.query(Chat)
            
            # Apply sorting
            sort_column = getattr(Chat, sort_by, Chat.created_at)
            if sort_order == "desc":
                query = query.order_by(sort_column.desc())
            else:
                query = query.order_by(sort_column.asc())
            
            # Get total count before pagination
            total_count = query.count()
            
            # Apply pagination
            offset = (page - 1) * page_size
            chats = query.offset(offset).limit(page_size).all()
            
            return {
                "items": [
                    {
                        "chat_id": str(chat.chat_id),
                        "created_at": chat.created_at,
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
