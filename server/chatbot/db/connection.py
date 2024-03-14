from typing import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    async_sessionmaker,
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from chatbot.config import DATABASE_URL

engine = create_async_engine(DATABASE_URL)
async_session = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(AsyncAttrs, DeclarativeBase):
    """Base model class"""

    pass


async def get_db() -> AsyncIterator[AsyncSession]:
    """Get DB connection as async generator, for FastAPI dependencies and post-processing"""
    db = async_session()
    yield db
    await db.close()
