from logging import getLogger
from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, status
from fastapi_pagination import Page
from sqlalchemy.ext.asyncio import AsyncSession
from chatbot.db.connection import get_db
from chatbot.db.model import Session, User
from chatbot.dto import SessionResult, SessionCreate
from chatbot.service import session as service, auth as auth_service
from chatbot.util.error import NotFoundError

logger = getLogger(__name__)

router = APIRouter(
    prefix="/session",
    tags=["session"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


@router.get("", response_model=Page[SessionResult])
async def get_list(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(auth_service.get_current_user)],
):
    """Get list of sessions"""
    logger.debug("get_list, user=%s", user)
    return await service.get_list(db, user.id)


@router.get("/{item_id}", response_model=SessionResult)
async def get(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(auth_service.get_current_user)],
    item_id: UUID,
):
    """Get session by id"""
    logger.debug("get, user=%s, item_id=%s", user, item_id)
    session: Session = await service.get(db, user.id, item_id)

    if session is None:
        raise NotFoundError()

    return session


@router.post("", response_model=SessionResult, status_code=status.HTTP_201_CREATED)
async def create(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(auth_service.get_current_user)],
    payload: SessionCreate,
):
    """Create session"""
    logger.debug("create, user=%s, payload=%s", user, payload)
    session: Session = await service.create(db, user.id, payload.title, payload.tool_id)
    return session


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(auth_service.get_current_user)],
    item_id: UUID,
):
    """Delete session by id"""
    await service.delete(db, user.id, item_id)
