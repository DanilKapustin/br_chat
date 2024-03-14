from logging import getLogger
from typing import Annotated, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, status, UploadFile
from fastapi_pagination import Page
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from chatbot.db import get_db
from chatbot.db.model import SourceType, SourceStatus, Source
from chatbot.dto import SourceResult, SourceCreate, SourceUpdate, SourceConfiguration
from chatbot.service import source as service
from chatbot.util.error import NotFoundError, BadRequestError
from chatbot.task import enqueue, index_source
from chatbot.service.source.upload import ALLOWED_FILE_EXTENSIONS

logger = getLogger(__name__)

router = APIRouter(
    prefix="/source",
    tags=["source"],
    dependencies=[],
    responses={status.HTTP_404_NOT_FOUND: {"description": "Not found"}},
)


@router.get("", response_model=Page[SourceResult])
async def get_list(db: Annotated[AsyncSession, Depends(get_db)]):
    """Get list of sources"""
    return await service.get_list(db)


@router.get("/{item_id}", response_model=SourceResult)
async def get(db: Annotated[AsyncSession, Depends(get_db)], item_id: UUID):
    """Get source by id"""
    logger.debug("get, item_id=%s", item_id)
    source: Source = await service.get(db, item_id)

    if source is None:
        raise NotFoundError()

    return source


@router.post("", response_model=SourceResult, status_code=status.HTTP_201_CREATED)
async def create(db: Annotated[AsyncSession, Depends(get_db)], payload: SourceCreate):
    """Create source"""
    logger.debug("create, payload=%s", payload)

    try:
        configuration: Optional[SourceConfiguration] = service.parse_configuration(
            payload.type, payload.configuration
        )
    except ValidationError as exc:
        logger.error("create, invalid configuration", exc_info=exc)
        raise BadRequestError("Invalid configuration") from exc

    result: Source = await service.create(
        db, payload.title, payload.description, payload.type, configuration
    )

    # start indexing right away after adding, if it's not an upload source
    if result.type != SourceType.UPLOAD:
        await enqueue(index_source, source_id=str(result.id))

    return result


@router.put("/{item_id}", response_model=SourceResult)
async def update(
    db: Annotated[AsyncSession, Depends(get_db)], item_id: UUID, payload: SourceUpdate
):
    """Update source"""
    logger.debug("update, item_id=%s, payload=%s", item_id, payload)
    source: Source = await service.get(db, item_id)

    if source is None:
        raise NotFoundError()

    if source.status not in (SourceStatus.ERROR, SourceStatus.FINISHED):
        raise BadRequestError("Invalid source status")

    try:
        configuration: Optional[SourceConfiguration] = service.parse_configuration(
            source.type, payload.configuration
        )
    except ValidationError as exc:
        logger.error("create, invalid configuration", exc_info=exc)
        raise BadRequestError("Invalid configuration") from exc

    return await service.update(
        db, source, payload.title, payload.description, configuration
    )


@router.post("/{item_id}/upload", response_model=SourceResult)
async def upload_file(
    db: Annotated[AsyncSession, Depends(get_db)], item_id: UUID, upload: UploadFile
):
    """Upload source file to UPLOAD types of sources"""
    logger.debug("upload_file, item_id=%s, upload=%s", item_id, upload.filename)
    source: Source = await service.get(db, item_id)

    if source is None:
        raise NotFoundError()

    if source.type != SourceType.UPLOAD:
        raise BadRequestError("Invalid source type")

    if source.status != SourceStatus.NEW:
        raise BadRequestError("Invalid source status")

    if upload.filename.split(".")[-1] not in ALLOWED_FILE_EXTENSIONS:
        raise BadRequestError("Invalid file type")

    source = await service.upload(db, source, upload)
    await enqueue(index_source, source_id=str(source.id))

    return source


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(db: Annotated[AsyncSession, Depends(get_db)], item_id: UUID):
    """Delete source by id"""
    logger.debug("delete, item_id=%s", item_id)
    await service.delete(db, item_id)


@router.post("/{item_id}/reindex", status_code=status.HTTP_204_NO_CONTENT)
async def reindex(db: Annotated[AsyncSession, Depends(get_db)], item_id: UUID):
    """Reindex source"""
    logger.debug("reindex, item_id=%s", item_id)
    source: Source = await service.get(db, item_id)

    if source is None:
        raise NotFoundError()

    if not source.can_be_reindexed:
        raise BadRequestError("Source cannot be reindexed")

    await enqueue(index_source, source_id=str(source.id), reindex=True)
