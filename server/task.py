from logging import config, getLogger
from os import environ
from typing import cast, List, Coroutine

from chatbot.knowledge import DocumentCollection
from chatbot.log import LogConfig
from chatbot.service.tool import ToolFactory
from chatbot.task import queue, index_source

config.dictConfig(LogConfig().dict())
logger = getLogger(__name__)


async def startup(ctx: dict):
    """Startup task"""
    logger.debug("startup, ctx=%s", ctx)
    DocumentCollection().create()


async def shutdown(ctx: dict):
    """Shutdown task"""
    logger.debug("shutdown, ctx=%s", ctx)


async def before_process(ctx: dict):
    """Before process task"""
    logger.debug("before_process, ctx=%s", ctx)


async def after_process(ctx: dict):
    """After process task"""
    logger.debug("after_process, ctx=%s", ctx)


settings = {
    "queue": queue,
    "functions": cast(List[Coroutine], [index_source])
    + list(ToolFactory().get_task_entry_points().values()),
    "concurrency": int(environ.get("BACKGROUND_WORKERS", "4")),
    "cron_jobs": [],
    "startup": startup,
    "shutdown": shutdown,
    "before_process": before_process,
    "after_process": after_process,
}
