from typing import Annotated

from fastapi import APIRouter, Depends
from logging import getLogger
from sqlalchemy.ext.asyncio import AsyncSession

from chatbot.db.connection import get_db
from chatbot.db.model import User
from chatbot.dto import StatsResult
from chatbot.service import stats as service, auth as auth_service

logger = getLogger(__name__)

router = APIRouter(
    prefix="/stats",
    tags=["stats"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


@router.get("", response_model=StatsResult)
async def get(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(auth_service.get_current_user)],
) -> StatsResult:
    """Get stats"""
    logger.debug("get, user=%s", user)
    return await service.get_stats(db, user.id)
