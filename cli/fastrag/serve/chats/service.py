from typing import override
from uuid import UUID

from fastrag.serve.chats.interfaces import IChatRepository, IChatService
from fastrag.serve.chats.model import Chat, ChatMessage
from fastrag.serve.chats.schemas import ChatMessageCreate
from fastrag.serve.paging import Page, PageParameters


class ChatService(IChatService):
    def __init__(self, repository: IChatRepository) -> None:
        self.repository = repository

    @override
    async def get_page(
        self,
        page_parameters: PageParameters,
    ) -> Page[Chat]:
        return await self.repository.get_chats(
            page_parameters,
        )

    @override
    async def get_chat(
        self,
        id: UUID,
        include_messages: bool = False,
    ) -> Chat | None:
        return await self.repository.get_chat(
            id=id,
            include_messages=include_messages,
        )

    @override
    async def save_message(
        self,
        data: ChatMessageCreate,
        ip: str | None = None,
        country: str | None = None,
    ) -> ChatMessage:
        return await self.repository.save_message(
            message=data,
            ip=ip,
            country=country,
        )
