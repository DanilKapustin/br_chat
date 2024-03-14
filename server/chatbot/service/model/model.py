from collections.abc import Generator
from contextlib import asynccontextmanager
from logging import getLogger
from typing import Sequence, Optional, List, Type, cast
from uuid import UUID, uuid4
from portalocker import Lock

from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import Result, select
from sqlalchemy.ext.asyncio import AsyncSession

from chatbot.db.model import Model, clone_model
from chatbot.dto import ModelConfiguration, ModelConfigurationFields
from .base import BaseModel
from .factory import ModelFactory

LOCK_NAME = "model.lock"

logger = getLogger(__name__)
model_lock: Lock = Lock(LOCK_NAME)


async def get_list(db: AsyncSession) -> Sequence[Model]:
    """Get list of models"""
    logger.debug("get_list")
    return await paginate(
        db,
        select(Model).order_by(
            Model.is_system.desc(), Model.name.asc(), Model.title.asc()
        ),
    )


async def get_all(db: AsyncSession) -> Sequence[Model]:
    """Get full list of models"""
    logger.debug("get_all")
    result: Result = await db.execute(select(Model).order_by(Model.name.asc()))

    return result.unique().scalars().all()


async def get_configuration_fields() -> List[ModelConfigurationFields]:
    """Get configuration fields for all model types"""
    logger.debug("get_configuration_fields")
    result: List[ModelConfigurationFields] = []

    for name, configuration_class in ModelFactory().get_configuration_classes().items():
        result.append(
            ModelConfigurationFields(name=name, fields=configuration_class.schema())
        )

    logger.debug("get_configuration_fields, result=%s", result)

    return result


async def get(db: AsyncSession, model_id: UUID) -> Model:
    """Get model by id"""
    logger.debug("get, model_id=%s", model_id)
    return await db.scalar(select(Model).filter(Model.id == model_id))


def parse_configuration(name: str, model_configuration: dict) -> ModelConfiguration:
    """Parse configuration"""
    logger.debug(
        "parse_configuration, name=%s, model_configuration=%s",
        name,
        model_configuration,
    )
    configuration_class: Type[ModelConfiguration] = cast(
        Type[ModelConfiguration], ModelFactory().get_configuration_class(name)
    )
    return configuration_class(**model_configuration)


@asynccontextmanager
async def get_model_instance(
    db: AsyncSession, model_id: UUID
) -> Generator[BaseModel, None, None]:
    """Get LLM instance"""
    logger.debug("get_model_instance, model_id=%s", model_id)

    model: Model = await get(db, model_id)

    if model is None:
        raise ValueError(f"Model with id {model_id} not found")

    configuration: ModelConfiguration = parse_configuration(
        model.name, model.configuration
    )

    model_class: Optional[Type[BaseModel]] = ModelFactory().get_model_class(model.name)

    if model_class is None:
        raise ValueError(f"Model not found: {model.name}")

    try:
        if model_class.IS_LOCAL:
            model_lock.acquire()
            logger.debug(
                "get_model_instance, model_class=%s, lock acquired", model_class
            )

        yield ModelFactory().get(model.name, configuration)

    finally:
        if model_class.IS_LOCAL:
            model_lock.release()
            logger.debug(
                "get_model_instance, model_class=%s, lock released", model_class
            )


async def create(
    db: AsyncSession,
    name: str,
    title: str,
    description: Optional[str],
    configuration: Optional[ModelConfiguration],
) -> Model:
    """Create model"""
    logger.debug(
        "create, name=%s, title=%s, description=%s, configuration=%s",
        name,
        title,
        description,
        configuration,
    )

    model: Model = Model(
        id=uuid4(),
        name=name,
        title=title,
        description=description,
        is_system=False,
        configuration=configuration.dict() if configuration is not None else None,
        created_by="admin",
        updated_by="admin",
    )

    db.add(model)
    await db.commit()
    await db.refresh(model)

    return model


async def update(
    db: AsyncSession,
    model: Model,
    title: str,
    description: str,
    configuration: ModelConfiguration,
) -> Model:
    """Update model"""
    logger.debug(
        "update, model=%s, title=%s, description=%s, configuration=%s",
        model,
        title,
        description,
        configuration,
    )
    model.title = title
    model.description = description
    model.configuration = configuration.dict() if configuration is not None else None

    db.add(model)
    await db.commit()
    await db.refresh(model)

    return model


async def duplicate(db: AsyncSession, model: Model) -> Model:
    """Duplicate model"""
    logger.debug("duplicate, model=%s", model)

    new_model: Model = Model(**clone_model(model))
    new_model.id = uuid4()
    new_model.title = f"{model.title} (copy)"
    new_model.is_system = False

    db.add(new_model)
    await db.commit()
    await db.refresh(new_model)

    return new_model


async def delete(db: AsyncSession, model_id: UUID):
    """Delete model"""
    logger.debug("delete, model_id=%s", model_id)
    model: Model = await get(db, model_id)

    if model is None or model.is_system:
        return

    await db.delete(model)
    await db.commit()
