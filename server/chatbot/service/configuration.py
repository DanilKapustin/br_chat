from typing import List, Sequence, Optional
from logging import getLogger
from uuid import uuid4
from sqlalchemy import Result, select
from sqlalchemy.ext.asyncio import AsyncSession
from chatbot.db.model.configuration import Config, Configuration, Language

DEFAULT_LANGUAGE = "en"

logger = getLogger(__name__)


async def get_list(db: AsyncSession) -> List[Configuration]:
    """Get all configuration entries"""
    logger.debug("get_list")

    query_result: Result = await db.execute(
        select(Configuration).order_by(Configuration.name.asc()))
    result: dict[Config, Configuration] = {
        cfg.name: cfg for cfg in query_result.scalars().all()}

    for cfg in Config:
        if cfg not in result:
            result[cfg] = Configuration(name=cfg, value=None)

    logger.debug("get_list, list=%s", result.values())

    return list(result.values())


async def get_by_name(db: AsyncSession, name: Config) -> Optional[str]:
    """Get single configuration value"""
    logger.debug("get_by_name, name=%s", name)
    value: Configuration = await db.scalar(select(Configuration)
                                           .where(Configuration.name == name))

    if value is None:
        logger.debug("get_by_name, value is None")
        return None

    logger.debug("get_by_name, value=%s", value)
    return value.value


async def update(db: AsyncSession, values: dict[str, str]):
    """Update configuration"""
    logger.debug("update, values=%s", values)

    for cfg in Config:
        current: Configuration = await db.scalar(select(Configuration)
                                                 .where(Configuration.name == cfg))

        if current is None:
            current = Configuration(
                id=uuid4(),
                name=cfg,
                value=values.get(cfg.name.lower(), None),
                created_by="admin",
                updated_by="admin")
        else:
            current.value = values.get(cfg.name.lower(), None)

        db.add(current)

    await db.commit()


async def get_language(db: AsyncSession) -> str:
    """Get language configuration"""
    logger.debug("get_language")
    language: str = await get_by_name(db, Config.LANGUAGE)

    if language is None:
        logger.warn("get_language, language is None, using default")
        return DEFAULT_LANGUAGE

    return language


async def get_embedding_model() -> str:
    """Get embedding model configuration"""
    logger.debug("get_embedding_model")
    return "E5"


async def get_language_list(db: AsyncSession) -> Sequence[Language]:
    """Get languages"""
    logger.debug("get_languages")
    result: Result = await db.execute(
        select(Language).order_by(Language.code.asc()))

    return result.scalars().all()
