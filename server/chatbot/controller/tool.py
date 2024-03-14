from typing import Annotated, Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, status
from fastapi_pagination import Page
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from chatbot.db.connection import get_db
from chatbot.db.model import Tool
from chatbot.dto import (
    ToolConfiguration,
    ToolCreate,
    ToolUpdate,
    ToolResult,
    ToolConfigurationFields,
)
from chatbot.service import tool as service
from chatbot.util.error import NotFoundError, BadRequestError


router = APIRouter(
    prefix="/tool",
    tags=["tool"],
    dependencies=[],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@router.get("", response_model=Page[ToolResult])
async def get_list(db: Annotated[AsyncSession, Depends(get_db)]):
    """Get list of tools"""
    return await service.get_list(db)


@router.get("/all", response_model=List[ToolResult])
async def get_all(db: Annotated[AsyncSession, Depends(get_db)]):
    """Get list of all tools"""
    return await service.get_all(db)


@router.get("/configuration-fields", response_model=List[ToolConfigurationFields])
async def get_configuration_fields():
    """Get configuration fields"""
    return await service.get_configuration_fields()


@router.get("/{item_id}", response_model=ToolResult)
async def get(db: Annotated[AsyncSession, Depends(get_db)], item_id: UUID):
    """Get tool by id"""
    tool: Tool = await service.get(db, item_id)

    if tool is None:
        raise NotFoundError()

    return tool


@router.post("", response_model=ToolResult, status_code=status.HTTP_201_CREATED)
async def create(db: Annotated[AsyncSession, Depends(get_db)], payload: ToolCreate):
    """Create tool"""
    try:
        configuration: Optional[ToolConfiguration] = service.parse_configuration(
            payload.name, payload.configuration
        )
    except ValidationError as exc:
        raise BadRequestError("Invalid configuration") from exc

    result: Tool = await service.create(
        db,
        payload.name,
        payload.title,
        payload.description,
        configuration,
        payload.model_id,
    )

    return result


@router.put("/{item_id}", response_model=ToolResult)
async def update(
    db: Annotated[AsyncSession, Depends(get_db)], item_id: UUID, payload: ToolUpdate
):
    """Update tool"""
    tool: Tool = await service.get(db, item_id)

    if tool is None:
        raise NotFoundError()

    try:
        configuration: Optional[ToolConfiguration] = service.parse_configuration(
            tool.name, payload.configuration
        )
    except ValidationError as exc:
        raise BadRequestError("Invalid configuration") from exc

    return await service.update(
        db, tool, payload.title, payload.description, configuration, payload.model_id
    )


@router.post("/{item_id}/duplicate", response_model=ToolResult)
async def duplicate(db: Annotated[AsyncSession, Depends(get_db)], item_id: UUID):
    """Duplicate tool by id"""
    tool: Tool = await service.get(db, item_id)

    if tool is None:
        raise NotFoundError()

    return await service.duplicate(db, tool)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(db: Annotated[AsyncSession, Depends(get_db)], item_id: UUID):
    """Delete tool by id"""
    await service.delete(db, item_id)
