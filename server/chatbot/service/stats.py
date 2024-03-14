from logging import getLogger

from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from chatbot.dto.stats import StatsResult, SessionStatsResult, MessageStatsResult
from chatbot.service.session import (
    session as session_service,
    message as message_service,
)

logger = getLogger(__name__)


async def get_stats(db: AsyncSession, user_id: UUID) -> StatsResult:
    """Get stats for the dashboard"""
    logger.debug("get_stats, user_id=%s", user_id)
    likes: int = await message_service.get_count(db, user_id, rating=5)
    dislikes: int = await message_service.get_count(db, user_id, rating=0)

    return StatsResult(
        sessions=SessionStatsResult(total=await session_service.get_count(db, user_id)),
        messages=MessageStatsResult(
            total=await message_service.get_count(db, user_id),
            likes=likes,
            dislikes=dislikes,
            regenerations=await message_service.get_count(db, user_id, is_hidden=True),
            ratings=likes + dislikes,
        ),
    )
