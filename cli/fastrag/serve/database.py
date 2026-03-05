import asyncio
import logging
from typing import Annotated, AsyncIterator

from fastapi import Depends
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from fastrag.config.settings import settings

logger = logging.getLogger(__name__)

sqlalchemy_url = settings.database_url.replace("postgresql://", "postgresql+asyncpg://", 1)

engine = create_async_engine(sqlalchemy_url, echo=False)
session_factory = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)


async def get_session(
    session_factory: Annotated[async_sessionmaker[AsyncSession], Depends(session_factory)],
) -> AsyncIterator[AsyncSession]:
    async with session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


class Base(DeclarativeBase): ...


async def initialize_database():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


async def wait_database(
    timeout: int = 5,
):
    while True:
        try:
            async with engine.connect():
                logger.info("Successfully connected to the database.")
                break
        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.exception(e)
            logger.info("Database not reachable, waiting %d seconds...", timeout)
            await asyncio.sleep(timeout)
