from logging import getLogger
from typing import Optional
from uuid import UUID
from saq.types import Context

from chatbot.service.source import source as service

logger = getLogger(__name__)


async def index_source(ctx: Context, *, source_id: UUID, reindex: Optional[bool] = False):
    """Index source and add it to vector store"""
    logger.debug("index_source, ctx=%s, source_id=%s, reindex=%s", ctx,
                 source_id, reindex)

    try:
        await service.index(source_id, reindex)
    except BaseException as error:
        logger.error("index_source, caught exception=%s",
                     error, exc_info=error)
        raise error

    logger.debug(
        "index_source, indexing finished, ctx=%s, source_id=%s, reindex=%s",
        ctx, source_id, reindex)
