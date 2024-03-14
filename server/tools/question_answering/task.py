from logging import getLogger
from uuid import UUID
from saq.types import Context

from .service import get_system_answer

logger = getLogger(__name__)


async def run_question_answering(ctx: Context, *, user_id: UUID, session_id: UUID):
    """Run question answering"""
    logger.debug(
        "run_question_answering, ctx=%s, user_id=%s, session_id=%s",
        ctx,
        user_id,
        session_id,
    )

    try:
        await get_system_answer(user_id, session_id)

    except BaseException as error:
        logger.error(
            "run_question_answering, caught exception=%s", error, exc_info=error
        )
        raise error

    logger.debug("run_question_answering, processing finished, ctx=%s", ctx)
