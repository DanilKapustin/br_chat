from asyncio import sleep
from logging import getLogger
from typing import Annotated, Sequence
from uuid import UUID

from fastapi import APIRouter, Depends, status, WebSocket
from redis.asyncio.client import PubSub
from sqlalchemy.ext.asyncio import AsyncSession
from websockets.exceptions import ConnectionClosedOK

from chatbot.db import get_db
from chatbot.db.model import Session, Message, User
from chatbot.dto import MessageResult
from chatbot.service import session as session_service, auth as auth_service
from chatbot.service.session import message as message_service
from chatbot.task import enqueue
from chatbot.util.error import NotFoundError
from .dto import MessageCreate, MessageRate
from .task import run_question_answering

logger = getLogger(__name__)

router = APIRouter(
    prefix="/session/{session_id}/tool/question_answering",
    tags=["tool: question answering"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


@router.get("", response_model=list[MessageResult])
async def get_messages(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(auth_service.get_current_user)],
    session_id: UUID,
    offset: int = 0,
    limit: int = 10,
) -> Sequence[Message]:
    """Get a list of messages"""
    logger.debug(
        "get_messages, user=%s, session_id=%s, offset=%s, limit=%s",
        user,
        session_id,
        offset,
        limit,
    )
    session: Session = await session_service.get(db, user.id, session_id)

    if session is None:
        raise NotFoundError()

    return await message_service.get_list(db, user.id, session_id, offset, limit, False)


@router.post("", response_model=MessageResult, status_code=status.HTTP_201_CREATED)
async def create(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(auth_service.get_current_user)],
    session_id: UUID,
    payload: MessageCreate,
) -> Message:
    """Create message"""
    logger.debug(
        "create, user=%s, session_id=%s, payload=%s", user, session_id, payload
    )
    session: Session = await session_service.get(db, user.id, session_id)

    if session is None:
        raise NotFoundError()

    message: Message = await message_service.create(
        db, user.id, session_id, payload.message
    )
    await enqueue(
        run_question_answering, user_id=str(user.id), session_id=str(session_id)
    )

    return message


@router.post(
    "/message/{message_id}/rate",
    response_model=MessageResult,
    status_code=status.HTTP_200_OK,
)
async def rate(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(auth_service.get_current_user)],
    session_id: UUID,
    message_id: UUID,
    payload: MessageRate,
) -> Message:
    """Rate a message"""
    logger.debug(
        "rate, user=%s, session_id=%s, message_id=%s, payload=%s",
        user,
        session_id,
        message_id,
        payload,
    )
    message: Message = await message_service.rate(
        db, user.id, session_id, message_id, payload.rating
    )

    if message is None:
        raise NotFoundError()

    return message


@router.post(
    "/message/{message_id}/regenerate",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def regenerate(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[User, Depends(auth_service.get_current_user)],
    session_id: UUID,
    message_id: UUID,
):
    """Rate a message"""
    logger.debug(
        "regenerate, user=%s, session_id=%s, message_id=%s",
        user,
        session_id,
        message_id,
    )
    message: Message = await message_service.regenerate(
        db, user.id, session_id, message_id
    )

    if message is None:
        raise NotFoundError()

    await enqueue(
        run_question_answering, user_id=str(user.id), session_id=str(session_id)
    )


@router.websocket("/ws")
async def get_new(
    db: Annotated[AsyncSession, Depends(get_db)],
    session_id: UUID,
    websocket: WebSocket,
):
    """Get new messages through websocket"""
    logger.debug("get_new, session_id=%s", session_id)
    session: Session = await session_service.get_by_id(db, session_id)

    if session is None:
        raise NotFoundError()

    await websocket.accept()
    channel: PubSub = await message_service.subscribe(session_id)

    try:
        while True:
            data: dict = await message_service.get_message_from_channel(channel)

            if data is None:
                logger.debug("get_new, no data in channel")

                # sending ping to track closed sockets
                await websocket.send_text("ping")
                await sleep(3.0)

                continue

            logger.debug("get_new, got data from channel: %s", data)
            message_json: str = data["data"]

            await websocket.send_text(message_json)

    except ConnectionClosedOK:
        logger.debug("get_new, websocket closed")

    finally:
        await websocket.close()
        await channel.close()
