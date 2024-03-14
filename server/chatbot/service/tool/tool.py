from logging import getLogger
from typing import Optional, Sequence, List, Type, cast
from uuid import UUID, uuid4

from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select, Result
from sqlalchemy.ext.asyncio import AsyncSession

from chatbot.db.model import Tool, clone_model
from chatbot.dto import ToolConfiguration, ToolConfigurationFields
from .base_event_handler import BaseEventHandler, EventHandlerMethod
from .factory import ToolFactory

logger = getLogger(__name__)


async def get_list(db: AsyncSession) -> Sequence[Tool]:
    """Get list of tools"""
    logger.debug("get_list")
    return await paginate(
        db,
        select(Tool).order_by(Tool.is_system.desc(), Tool.name.asc(), Tool.title.asc()),
    )


async def get_all(db: AsyncSession) -> Sequence[Tool]:
    """Get full list of tools"""
    logger.debug("get_all")
    result: Result = await db.execute(select(Tool).order_by(Tool.title.asc()))

    return result.unique().scalars().all()


async def get_configuration_fields() -> List[ToolConfigurationFields]:
    """Get configuration fields for all tool types"""
    logger.debug("get_configuration_fields")
    result: List[ToolConfigurationFields] = []

    for name, configuration_class in ToolFactory().get_configuration_classes().items():
        result.append(
            ToolConfigurationFields(name=name, fields=configuration_class.schema())
        )

    logger.debug("get_configuration_fields, result=%s", result)

    return result


async def get(db: AsyncSession, tool_id: UUID) -> Tool:
    """Get tool by id"""
    logger.debug("get, tool_id=%s", tool_id)
    return await db.scalar(select(Tool).filter(Tool.id == tool_id))


def _get_event_handler(tool: Tool) -> BaseEventHandler:
    """Get event handler"""
    logger.debug("get_event_handler, tool=%s", tool)
    event_handler: BaseEventHandler = ToolFactory().get_event_handler(tool.name)

    return event_handler


async def emit(db: AsyncSession, tool_id: UUID, event_name: str, **kwargs):
    """Emit event"""
    logger.debug(
        "emit, tool_id=%s, event_name=%s, kwargs=%s", tool_id, event_name, kwargs
    )
    tool: Tool = await get(db, tool_id)

    if tool is None:
        raise RuntimeError("Tool not found")

    event_handler: BaseEventHandler = _get_event_handler(tool)
    event_handler_method: Optional[EventHandlerMethod] = getattr(
        event_handler, event_name, None
    )

    if event_handler_method is None:
        raise RuntimeError(f"Event handler method not found for event {event_name}")

    await event_handler_method(event_handler, **kwargs)


def parse_configuration(name: str, tool_configuration: dict) -> ToolConfiguration:
    """Parse configuration"""
    logger.debug(
        "parse_configuration, name=%s, tool_configuration=%s", name, tool_configuration
    )
    configuration_class: Type[ToolConfiguration] = cast(
        Type[ToolConfiguration], ToolFactory().get_configuration_class(name)
    )
    return configuration_class(**tool_configuration)


async def create(
    db: AsyncSession,
    name: str,
    title: str,
    description: Optional[str],
    configuration: Optional[ToolConfiguration],
    model_id: UUID,
) -> Tool:
    """Create tool"""
    logger.debug(
        "create, name=%s, title=%s, description=%s, configuration=%s, model_id=%s",
        name,
        title,
        description,
        configuration,
        model_id,
    )

    tool: Tool = Tool(
        id=uuid4(),
        name=name,
        title=title,
        description=description,
        configuration=configuration.dict() if configuration is not None else None,
        model_id=model_id,
        is_system=False,
        created_by="admin",
        updated_by="admin",
    )

    db.add(tool)
    await db.commit()
    await db.refresh(tool)

    return tool


async def update(
    db: AsyncSession,
    tool: Tool,
    title: str,
    description: Optional[str],
    configuration: Optional[ToolConfiguration],
    model_id: UUID,
) -> Tool:
    """Update tool"""
    logger.debug(
        "update, tool=%s, title=%s, description=%s, configuration=%s, model_id=%s",
        tool,
        title,
        description,
        configuration,
        model_id,
    )

    tool.title = title
    tool.description = description
    tool.configuration = configuration.dict() if configuration is not None else None
    tool.model_id = model_id

    db.add(tool)
    await db.commit()
    await db.refresh(tool)

    return tool


async def duplicate(db: AsyncSession, tool: Tool) -> Tool:
    """Duplicate tool"""
    logger.debug("duplicate, tool=%s", tool)

    new_tool: Tool = Tool(**clone_model(tool))
    new_tool.id = uuid4()
    new_tool.title = f"{tool.title} (copy)"
    new_tool.is_system = False

    db.add(new_tool)
    await db.commit()
    await db.refresh(new_tool)

    return new_tool


async def delete(db: AsyncSession, tool_id: UUID):
    """Delete tool"""
    logger.debug("delete, tool_id=%s", tool_id)
    tool: Tool = await get(db, tool_id)

    if tool is None or tool.is_system:
        return

    await db.delete(tool)
    await db.commit()
