from datetime import datetime

from sqlalchemy import Column, DateTime, String, Text

from .database import Base


class ChatMessage(Base):
    __tablename__ = "chat_message"

    id = Column(String, primary_key=True, index=True, nullable=False, unique=True, default=None)
    chat_id = Column(String, index=True, nullable=False)
    message = Column(Text, nullable=False)
    role = Column(String, nullable=False)
    meta = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
