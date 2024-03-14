from logging import getLogger
from typing import List, Sequence, Optional
from uuid import uuid4, UUID

from redis.asyncio.client import PubSub
from sqlalchemy import select, Result, Select, func
from sqlalchemy.ext.asyncio import AsyncSession

from chatbot.db.model import Message, MessageSource, Session
from chatbot.dto import KnowledgeResult
from chatbot.util import channel
from .session import get as get_session

logger = getLogger(__name__)


async def get_list(
    db: AsyncSession,
    user_id: UUID,
    session_id: UUID,
    offset: int,
    limit: int,
    is_hidden: Optional[bool],
) -> Sequence[Message]:
    """Get list of messages"""
    logger.debug(
        "get_list, user_id=%s, session_id=%s, offset=%s, limit=%s, is_hidden=%s",
        session_id,
        offset,
        limit,
        is_hidden,
    )

    session: Session = await get_session(db, user_id, session_id)

    if session is None:
        return []

    query: Select = select(Message).where(Message.session_id == session_id)

    if is_hidden is not None:
        query = query.where(Message.is_hidden == is_hidden)

    result: Result = await db.execute(
        query.offset(offset).limit(limit).order_by(Message.created_at.asc())
    )

    return result.unique().scalars().all()


async def get_count(
    db: AsyncSession,
    user_id: UUID,
    rating: Optional[int] = None,
    is_hidden: Optional[bool] = None,
) -> int:
    """Get count of messages"""
    logger.debug(
        "get_count, user_id=%s, rating=%s, is_hidden=%s", user_id, rating, is_hidden
    )
    query: Select = select(func.count())

    if rating is not None:
        query = query.where(Message.rating == rating)

    if is_hidden is not None:
        query = query.where(Message.is_hidden == is_hidden)

    query = query.where(Message.is_system == True, Message.user_id == user_id)

    return await db.scalar(query.select_from(Message))


async def create(
    db: AsyncSession,
    user_id: UUID,
    session_id: UUID,
    message: str,
    author: Optional[str] = None,
    sources: Optional[List[MessageSource]] = None,
    is_system: bool = False,
) -> Message:
    """Create message"""
    logger.debug(
        "create, user_id=%s, session_id=%s, message=%s, author=%s, sources=%s, is_system=%s",
        user_id,
        session_id,
        message,
        author,
        sources,
        is_system,
    )

    if sources is None:
        sources = []

    if author is None:
        author = "system" if is_system else "user"

    message: Message = Message(
        id=uuid4(),
        user_id=user_id,
        session_id=session_id,
        message=message,
        is_system=is_system,
        created_by=author,
        sources=sources,
        is_hidden=False,
    )

    db.add(message)
    await db.commit()
    await db.refresh(message)

    return message


async def subscribe(session_id: UUID) -> PubSub:
    """Subscribe message channel"""
    logger.debug("subscribe, session_id: %s", session_id)
    return await channel.subscribe("session_" + str(session_id))


async def get_message_from_channel(channel_handler: PubSub) -> Optional[dict]:
    """Get a message from the given channel handler."""
    return await channel_handler.get_message(ignore_subscribe_messages=True)


async def publish(session_id: UUID, message: str):
    """Publish message to channel"""
    logger.debug("publish, session_id: %s, message: %s", session_id, message)
    await channel.publish("session_" + str(session_id), message)


async def save_answer(
    db: AsyncSession,
    user_id: UUID,
    session_id: UUID,
    answer: str,
    sources: list[KnowledgeResult],
) -> Message:
    """Save answer"""
    logger.debug(
        "_save_answer, user_id=%s, session_id=%s, answer=%s, sources=%s",
        user_id,
        session_id,
        answer,
        sources,
    )

    # filter sources to have only unique URL values
    source_urls: set[str] = set()
    filtered_sources: list[KnowledgeResult] = []

    for source in sources:
        if source.url not in source_urls:
            source_urls.add(source.url)
            filtered_sources.append(source)

    message_sources: list[MessageSource] = [
        MessageSource(id=uuid4(), **s.dict(exclude={"id", "text"}))
        for s in filtered_sources
    ]
    message: Message = await create(
        db, user_id, session_id, answer, sources=message_sources, is_system=True
    )

    return message


async def rate(
    db: AsyncSession, user_id: UUID, session_id: UUID, message_id: UUID, rating: int
) -> Message:
    """Rate a message"""
    logger.debug(
        "rate, user_id=%s, session_id=%s, message_id=%s, rating=%s",
        user_id,
        session_id,
        message_id,
        rating,
    )

    message: Message = await db.scalar(
        select(Message).filter(
            Message.id == message_id,
            Message.user_id == user_id,
            Message.session_id == session_id,
            Message.is_system == True,
            Message.is_hidden == False,
        )
    )

    if message is None:
        raise ValueError("Message not found")

    message.rating = rating
    await db.commit()
    await db.refresh(message)

    return message


async def regenerate(
    db: AsyncSession, user_id: UUID, session_id: UUID, message_id: UUID
) -> Message:
    """Regenerate a message"""
    logger.debug(
        "regenerate, user_id=%s, session_id=%s, message_id=%s",
        user_id,
        session_id,
        message_id,
    )

    message: Message = await db.scalar(
        select(Message).filter(
            Message.id == message_id,
            Message.user_id == user_id,
            Message.session_id == session_id,
            Message.is_system == True,
            Message.is_hidden == False,
        )
    )

    if message is None:
        raise ValueError("Message not found")

    # treat this response as bad
    message.rating = 0
    message.is_hidden = True

    await db.commit()
    await db.refresh(message)

    return message
