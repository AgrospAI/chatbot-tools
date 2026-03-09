from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from fastrag.serve.chats.deps import get_chat_service
from fastrag.serve.chats.interfaces import IChatService
from fastrag.serve.chats.service import ChatService
from fastrag.serve.paging import PageParameters

router = APIRouter(prefix="/chats", tags=["chat"])


@router.get("/")
async def get_chats(
    chat_service: Annotated[IChatService, Depends(get_chat_service)],
    pagination: Annotated[PageParameters, Depends()],
):
    """Get all chats (no messages) with pagination and sorting."""

    return await chat_service.get_page(pagination)


@router.get("/{chat_id}")
async def get(
    chat_service: Annotated[ChatService, Depends(get_chat_service)],
    chat_id: UUID,
    include_messages: bool = True,
):
    """Get a specific chat"""
    chat = await chat_service.get_chat(
        id=chat_id,
        include_messages=include_messages,
    )

    if chat is None:
        raise HTTPException(status_code=404, detail="Chat not found")

    return chat
