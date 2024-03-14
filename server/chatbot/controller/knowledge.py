from logging import getLogger
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from fastapi_pagination import Page

from chatbot.dto import KnowledgeResult
from chatbot.knowledge import DocumentCollection, get_collection
from chatbot.service import knowledge as service
from chatbot.util.error import NotFoundError

logger = getLogger(__name__)

router = APIRouter(
    prefix="/knowledge",
    tags=["knowledge"],
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


@router.get("", response_model=Page[KnowledgeResult])
async def get_list(
    collection: Annotated[DocumentCollection, Depends(get_collection)],
    page: Annotated[int, Query(ge=1)] = 1,
    size: Annotated[int, Query(ge=1, le=100)] = 50,
):
    """Get document list"""
    logger.debug("get_list, page=%s, size=%s", page, size)
    return await service.get_list(collection, page, size)


@router.get("/{item_id}", response_model=KnowledgeResult)
async def get(
    collection: Annotated[DocumentCollection, Depends(get_collection)],
    item_id: UUID,
):
    """Get single document from collection by id"""
    knowledge: KnowledgeResult = await service.get(collection, item_id)

    if knowledge is None:
        raise NotFoundError()

    return knowledge


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(
    collection: Annotated[DocumentCollection, Depends(get_collection)],
    item_id: UUID,
):
    """Delete document"""
    await service.delete(collection, item_id)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_all(
    collection: Annotated[DocumentCollection, Depends(get_collection)]
):
    """Delete all documents"""
    await service.delete_all(collection)
