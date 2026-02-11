from typing import List
from uuid import UUID

from fastapi import Depends

from fastrag.serve.chats.model import Chat
from fastrag.serve.chats.repository import ChatRepository, get_chat_repository


class ChatService:
    chatRepository: ChatRepository

    def __init__(self, chatRepository: ChatRepository = Depends()):
        self.chatRepository = chatRepository

    def list(
        self,
        page: int,
        page_size: int,
        sort_by: str,
        sort_order: str,
    ) -> List[Chat]:
        return self.chatRepository.get_chats(
            page=page, page_size=page_size, sort_by=sort_by, sort_order=sort_order
        )

    def get(self, chat_id: UUID) -> Chat | None:
        return self.chatRepository.get_chat_by_id(chat_id)

    def save_message(
        self,
        chat_id: str,
        content: str,
        role: str,
        ip: str | None = None,
        country: str | None = None,
        sources: List[str] | None = None,
    ) -> None:
        self.chatRepository.save_message(
            chat_id=chat_id,
            content=content,
            role=role,
            ip=ip,
            country=country,
            sources=sources,
        )


def get_chat_service(
    chatRepository: ChatRepository = Depends(get_chat_repository),
) -> ChatService:
    return ChatService(chatRepository)
