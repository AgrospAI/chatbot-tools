from typing import override
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from fastrag.serve.chats.interfaces import IChatRepository
from fastrag.serve.chats.model import Chat, ChatMessage
from fastrag.serve.chats.schemas import ChatMessageCreate
from fastrag.serve.paging import Page, PageParameters


class ChatRepository(IChatRepository):
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    @override
    async def get_chat(
        self,
        id: UUID,
        include_messages: bool = True,
    ) -> Chat | None:
        query = select(Chat).filter(Chat.chat_id == id)

        if include_messages:
            query = query.options(selectinload(Chat.messages))

        result = await self.db.execute(query)
        return result.scalars().first()

    @override
    async def save_message(
        self,
        message: ChatMessageCreate,
        ip: str | None = None,
        country: str | None = None,
    ) -> ChatMessage:
        result = await self.db.execute(
            select(Chat).filter(Chat.chat_id == message.chat_id).limit(1)
        )

        chat = result.scalars().first()
        if not chat:
            chat = Chat(
                chat_id=message.chat_id,
                ip=ip,
                country=country,
            )
            self.db.add(chat)
            await self.db.flush()

        chat_msg = ChatMessage(
            chat_id=message.chat_id,
            content=message.content,
            role=message.role,
            sources=message.sources,
        )
        self.db.add(chat_msg)
        await self.db.commit()
        await self.db.refresh(chat_msg)

        return chat_msg

    @override
    async def get_chats(
        self,
        pagination: PageParameters,
    ) -> Page[Chat]:
        sort_column = getattr(
            Chat,
            pagination.sort_by,
            Chat.created_at,
        )
        sort = sort_column.desc() if pagination.sort_order == "desc" else sort_column.asc()

        total_count = await self.db.scalar(select(func.count()).select_from(Chat))

        result = await self.db.execute(
            select(Chat).order_by(sort).offset(pagination.offset).limit(pagination.page_size)
        )
        chats = result.scalars().all()

        return Page(
            items=chats,
            total=total_count,
            page=pagination.page,
            page_size=pagination.page_size,
        )
