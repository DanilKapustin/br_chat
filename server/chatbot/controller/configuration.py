from typing import Annotated, List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from chatbot.db.connection import get_db
from chatbot.dto import ConfigurationResult, ConfigurationUpdate, LanguageResult
from chatbot.service import configuration as service


router = APIRouter(
    prefix="/configuration",
    tags=["configuration"],
    dependencies=[],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@router.get("", response_model=List[ConfigurationResult])
async def get_list(db: Annotated[AsyncSession, Depends(get_db)]):
    """Get list of configuration entries"""
    return await service.get_list(db)


@router.get("/language", response_model=List[LanguageResult])
async def get_language_list(db: Annotated[AsyncSession, Depends(get_db)]):
    """Get list of languages"""
    return await service.get_language_list(db)


@router.put("", status_code=status.HTTP_204_NO_CONTENT)
async def update(
    db: Annotated[AsyncSession, Depends(get_db)], payload: ConfigurationUpdate
):
    """Update configuration"""
    await service.update(db, payload.dict())
