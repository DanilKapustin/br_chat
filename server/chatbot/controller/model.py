from typing import Annotated, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, status
from fastapi_pagination import Page
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from chatbot.db.connection import get_db
from chatbot.db.model import Model
from chatbot.dto import (
    ModelCreate,
    ModelUpdate,
    ModelResult,
    ModelConfiguration,
    ModelConfigurationFields,
)
from chatbot.service import model as service
from chatbot.util.error import NotFoundError, BadRequestError


router = APIRouter(
    prefix="/model",
    tags=["model"],
    dependencies=[],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@router.get("", response_model=Page[ModelResult])
async def get_list(db: Annotated[AsyncSession, Depends(get_db)]):
    """Get list of models"""
    return await service.get_list(db)


@router.get("/all", response_model=List[ModelResult])
async def get_all(db: Annotated[AsyncSession, Depends(get_db)]):
    """Get list of all models"""
    return await service.get_all(db)


@router.get("/configuration-fields", response_model=List[ModelConfigurationFields])
async def get_configuration_fields():
    """Get configuration fields"""
    return await service.get_configuration_fields()


@router.get("/{item_id}", response_model=ModelResult)
async def get(db: Annotated[AsyncSession, Depends(get_db)], item_id: UUID):
    """Get model by id"""
    model: Model = await service.get(db, item_id)

    if model is None:
        raise NotFoundError()

    return model


@router.post("", response_model=ModelResult, status_code=status.HTTP_201_CREATED)
async def create(db: Annotated[AsyncSession, Depends(get_db)], payload: ModelCreate):
    """Create model"""
    try:
        configuration: Optional[ModelConfiguration] = service.parse_configuration(
            payload.name, payload.configuration
        )
    except ValidationError as exc:
        raise BadRequestError("Invalid configuration") from exc

    return await service.create(
        db, payload.name, payload.title, payload.description, configuration
    )


@router.put("/{item_id}", response_model=ModelResult)
async def update(
    db: Annotated[AsyncSession, Depends(get_db)], item_id: UUID, payload: ModelUpdate
):
    """Update model"""
    model: Model = await service.get(db, item_id)

    if model is None:
        raise NotFoundError()

    try:
        configuration: Optional[ModelConfiguration] = service.parse_configuration(
            model.name, payload.configuration
        )
    except ValidationError as exc:
        raise BadRequestError("Invalid configuration") from exc

    return await service.update(
        db, model, payload.title, payload.description, configuration
    )


@router.post("/{item_id}/duplicate", response_model=ModelResult)
async def duplicate(db: Annotated[AsyncSession, Depends(get_db)], item_id: UUID):
    """Duplicate model by id"""
    model: Model = await service.get(db, item_id)

    if model is None:
        raise NotFoundError()

    return await service.duplicate(db, model)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(db: Annotated[AsyncSession, Depends(get_db)], item_id: UUID):
    """Delete model by id"""
    await service.delete(db, item_id)
