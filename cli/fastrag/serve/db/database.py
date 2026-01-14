from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from fastrag.config.settings import settings

# Only support Postgres for now, fail otherwise
if not settings.database_url.startswith("postgresql://"):
    raise ValueError("Only PostgreSQL is supported. Set a valid DATABASE_URL.")

# SQLAlchemy expects the URL in the format 'postgresql+psycopg2://...'
sqlalchemy_url = settings.database_url.replace("postgresql://", "postgresql+psycopg2://", 1)

engine = create_engine(sqlalchemy_url, echo=False, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
