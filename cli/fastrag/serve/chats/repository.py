from dataclasses import dataclass
from typing import Any, Dict, List
from uuid import UUID

from fastapi import Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from fastrag.serve.chats.model import Chat, ChatMessage
from fastrag.serve.database import get_session


@dataclass(frozen=True)
class ChatRepository:
    db: AsyncSession

    async def get_chat_by_id(
        self,
        chat_id: UUID,
    ) -> Dict[str, Any] | None:
        result = await self.db.execute(select(Chat).filter(Chat.chat_id == chat_id))
        chat = result.first()

        if not chat:
            return None

        result = await self.db.execute(
            select(ChatMessage)
            .filter(ChatMessage.chat_id == chat_id)
            .order_by(ChatMessage.created_at)
        )

        messages = result.scalars().all()

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

    async def save_message(
        self,
        chat_id: UUID,
        content: str,
        role: str,
        sources: List[str] | None = None,
        ip: str | None = None,
        country: str | None = None,
    ) -> None:
        result = await self.db.execute(select(Chat).filter(Chat.chat_id == chat_id).limit(1))

        chat = result.first()
        if not chat:
            chat = Chat()
            if hasattr(chat, "chat_id"):
                chat.chat_id = chat_id
            if hasattr(chat, "ip"):
                chat.ip = ip
            if hasattr(chat, "country"):
                chat.country = country
            self.db.add(chat)
            await self.db.flush()
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
        await self.db.commit()

    async def get_chats(
        self,
        page: int = 1,
        page_size: int = 10,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> Dict[str, Any]:
        sort_column = getattr(Chat, sort_by, Chat.created_at)

        query = select(Chat)

        if sort_order == "desc" and hasattr(sort_column, "desc"):
            query = query.order_by(sort_column.desc())
        elif hasattr(sort_column, "asc"):
            query = query.order_by(sort_column.asc())

        total_count = await self.db.scalar(select(func.count()).select_from(Chat))

        offset = (page - 1) * page_size
        result = await self.db.execute(query.offset(offset).limit(page_size))
        chats = result.scalars().all()

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


def get_chat_repository(db: AsyncSession = Depends(get_session)) -> ChatRepository:
    return ChatRepository(db)
