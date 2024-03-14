from logging import getLogger
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from chatbot.db import get_db
from chatbot.service.session import message as message_service
from chatbot.service.tool.base_event_handler import BaseEventHandler
from chatbot.task import enqueue
from .task import run_question_answering

logger = getLogger(__name__)


class EventHandler(BaseEventHandler):
    """Event handler"""

    async def on_session_created(self, user_id: UUID, session_id: UUID, message: str):
        """Called when a new session is created"""
        logger.debug(
            "on_session_created, user_id=%s, session_id=%s, message=%s",
            user_id,
            session_id,
            message,
        )
        db: AsyncSession = await anext(get_db())

        await message_service.create(db, user_id, session_id, message)
        await enqueue(
            run_question_answering, user_id=str(user_id), session_id=str(session_id)
        )

    async def on_session_finished(self, user_id: UUID, session_id: UUID):
        """Called when a session is finished"""
        logger.debug(
            "on_session_finished, user_id=%s, session_id=%s", user_id, session_id
        )
