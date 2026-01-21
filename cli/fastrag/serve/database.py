from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from fastrag.config.settings import settings

sqlalchemy_url = settings.database_url.replace("postgresql://", "postgresql+psycopg2://", 1)
engine = create_engine(sqlalchemy_url, echo=False, future=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = scoped_session(SessionLocal)
    try:
        yield db
    finally:
        db.close()


Base = declarative_base()


def initialize_database():
    Base.metadata.create_all(bind=engine)
