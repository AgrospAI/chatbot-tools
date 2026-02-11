import uuid
from datetime import datetime

from sqlalchemy import (
    ARRAY,
    BigInteger,
    CheckConstraint,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from fastrag.serve.database import Base


class Chat(Base):
    __tablename__ = "chats"

    chat_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    ip = Column(Text, nullable=True)
    country = Column(Text, nullable=True)
    messages = relationship("ChatMessage", back_populates="chat", cascade="all, delete-orphan")


class ChatMessage(Base):
    __tablename__ = "messages"

    message_id = Column(BigInteger, primary_key=True, autoincrement=True)
    chat_id = Column(
        UUID(as_uuid=True),
        ForeignKey("chats.chat_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    sources = Column(ARRAY(Text), nullable=True)
    chat = relationship("Chat", back_populates="messages")

    __table_args__ = (
        CheckConstraint("role IN ('user', 'assistant', 'system')", name="role_check"),
        Index("ix_chat_message_chat_id_created_at", "chat_id", "created_at"),
    )
