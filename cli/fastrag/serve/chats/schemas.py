from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


# --- Chat Message ---
class ChatMessageBase(BaseModel):
    role: Literal["user", "assistant", "system"]
    content: str
    sources: list[str] | None = None
    chat_id: UUID


class ChatMessageCreate(ChatMessageBase):
    pass


class ChatMessageResponse(ChatMessageBase):
    message_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Chat ---
class ChatBase(BaseModel):
    ip: str | None = None
    country: str | None = None
    chat_id: UUID


class ChatCreate(ChatBase):
    pass


class ChatResponse(ChatBase):
    chat_id: UUID
    created_at: datetime
    messages: list[ChatMessageResponse] = []

    model_config = ConfigDict(from_attributes=True)
