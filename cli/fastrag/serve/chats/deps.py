from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from fastrag.serve.chats.repository import ChatRepository
from fastrag.serve.chats.service import ChatService
from fastrag.serve.database import get_session


def get_chat_repository(
    db: AsyncSession = Depends(get_session),
) -> ChatRepository:
    return ChatRepository(db)


def get_chat_service(
    repository: ChatRepository = Depends(get_chat_repository),
) -> ChatService:
    return ChatService(repository)
