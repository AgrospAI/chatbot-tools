from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from fastrag.serve.chats.service import ChatService, get_chat_service

ChatRouter = APIRouter(prefix="/chats", tags=["chat"])


@ChatRouter.get("/")
def list(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    sort_by: str = Query("created_at", description="Field to sort by"),
    sort_order: str = Query("desc", description="Sort order: 'asc' or 'desc'"),
    chatService: ChatService = Depends(get_chat_service),
):
    """Get all chats (no messages) with pagination and sorting."""
    return chatService.list(page, page_size, sort_by, sort_order)


@ChatRouter.get("/{chat_id}")
def get(chat_id: UUID, chatService: ChatService = Depends(get_chat_service)):
    """Get a specific chat and all its messages."""
    chat = chatService.get(chat_id)

    if chat is None:
        raise HTTPException(status_code=404, detail="Chat not found")

    return chat
