from uuid import UUID

from fastapi import APIRouter, HTTPException, Query

from fastrag.serve.db import get_chat_repository, init_db

router = APIRouter()
init_db()
chat_repo = get_chat_repository()


@router.get("/chats")
def get_all_chats(
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    page_size: int = Query(10, ge=1, le=100, description="Number of items per page"),
    sort_by: str = Query("created_at", description="Field to sort by"),
    sort_order: str = Query("desc", description="Sort order: 'asc' or 'desc'"),
):
    """Get all chats (no messages) with pagination and sorting."""
    return chat_repo.get_chats(page=page, page_size=page_size, sort_by=sort_by, sort_order=sort_order)


@router.get("/chats/{chat_id}")
def get_chat_by_id(chat_id: UUID):
    """Get a specific chat and all its messages."""
    chat = chat_repo.get_chat_by_id(chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat
