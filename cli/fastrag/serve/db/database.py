from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

_engine = None
_SessionLocal = None
_Base = None


def get_db(settings):
    """
    Lazily instantiate and return the database engine, sessionmaker, and base.
    Only supports PostgreSQL.
    """
    import logging

    global _engine, _SessionLocal, _Base
    try:
        if _engine is None or _SessionLocal is None or _Base is None:
            if not settings.database_url.startswith("postgresql://"):
                logging.error("Only PostgreSQL is supported. Set a valid DATABASE_URL.")
                return None, None, None
            sqlalchemy_url = settings.database_url.replace(
                "postgresql://", "postgresql+psycopg2://", 1
            )
            try:
                _engine = create_engine(sqlalchemy_url, echo=False, future=True)
                _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
                _Base = declarative_base()
            except Exception as e:
                logging.error(f"Error initializing database: {e}")
                _engine, _SessionLocal, _Base = None, None, None
        return _engine, _SessionLocal, _Base
    except Exception as e:
        logging.error(f"Unexpected error in get_db: {e}")
        return None, None, None
