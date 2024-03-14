import uuid
from logging import getLogger
from typing import Sequence
from uuid import UUID

from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from chatbot.db.model import Session
from chatbot.service import tool as tool_service
from chatbot.util.string import first_n_words

logger = getLogger(__name__)


async def get_list(db: AsyncSession, user_id: UUID) -> Sequence[Session]:
    """Get list of sessions"""
    logger.debug("get_list, user_id=%s", user_id)
    return await paginate(
        db,
        select(Session)
        .filter(Session.user_id == user_id)
        .order_by(Session.created_at.desc()),
    )


async def get_by_id(db: AsyncSession, session_id: UUID) -> Session:
    """Get session by id"""
    logger.debug("get_by_id, session_id=%s", session_id)
    return await db.scalar(select(Session).filter(Session.id == session_id))


async def get(db: AsyncSession, user_id: UUID, session_id: UUID) -> Session:
    """Get session by id"""
    logger.debug("get, user_id=%s, session_id=%s", user_id, session_id)
    return await db.scalar(
        select(Session).filter(Session.id == session_id, Session.user_id == user_id)
    )


async def get_count(db: AsyncSession, user_id: UUID) -> int:
    """Get count of sessions"""
    logger.debug("get_count, user_id=%s", user_id)
    return await db.scalar(
        select(func.count()).filter(Session.user_id == user_id).select_from(Session)
    )


async def create(
    db: AsyncSession, user_id: UUID, message: str, tool_id: UUID
) -> Session:
    """Create session"""
    logger.debug(
        "create, user_id=%s, message=%s, tool_id=%s", user_id, message, tool_id
    )
    title: str = first_n_words(message, 5)

    if len(title) < len(message):
        title += "..."

    session: Session = Session(
        id=uuid.uuid4(),
        user_id=user_id,
        tool_id=tool_id,
        title=title,
        created_by="admin",
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)

    await tool_service.emit(
        db,
        tool_id,
        "on_session_created",
        user_id=user_id,
        session_id=session.id,
        message=message,
    )

    return session


async def delete(db: AsyncSession, user_id: UUID, session_id: UUID):
    """Delete session"""
    session: Session = await get(db, user_id, session_id)

    if session is None:
        return

    await db.delete(session)
    await db.commit()
