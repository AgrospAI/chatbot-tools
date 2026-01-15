from .database import Base, engine
from .repositories.sqlalchemy_repository import SQLAlchemyChatRepository


def init_db():
    Base.metadata.create_all(bind=engine)


def get_chat_repository():
    return SQLAlchemyChatRepository()
