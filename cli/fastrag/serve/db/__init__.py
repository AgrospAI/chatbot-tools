from fastrag.config import settings

from .database import get_db
from .repositories.sqlalchemy_repository import SQLAlchemyChatRepository


def init_db():
    engine, _, Base = get_db(settings)
    if Base is not None:
        Base.metadata.create_all(bind=engine)


def get_chat_repository():
    return SQLAlchemyChatRepository()
