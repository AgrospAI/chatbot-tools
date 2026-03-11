import asyncio
from typing import AsyncIterator

from fastapi.concurrency import asynccontextmanager
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from fastrag.config.settings import get_settings

settings = get_settings()

sqlalchemy_url = settings.database_url.replace(
    "postgresql://",
    "postgresql+asyncpg://",
    1,
)

engine = create_async_engine(
    sqlalchemy_url,
    echo=False,
)

session_factory = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


@asynccontextmanager
async def get_session() -> AsyncIterator[AsyncSession]:
    async with session_factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


class Base(DeclarativeBase): ...


is_initialized = False
_init_lock = asyncio.Lock()


async def initialize_database() -> None:
    global is_initialized

    if is_initialized:
        return

    async with _init_lock:
        if is_initialized:
            return

        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

        is_initialized = True
