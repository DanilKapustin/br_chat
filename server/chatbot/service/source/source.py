import uuid
from datetime import datetime
from logging import getLogger
from typing import Sequence, Optional
from uuid import UUID
from fastapi import UploadFile
from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from chatbot.db.connection import get_db
from chatbot.db.model import Source, SourceProgress, SourceStatus, SourceType
from chatbot.dto import SourceConfiguration, JiraConfiguration, ConfluenceConfiguration
from .upload import save_file, index as index_upload

logger = getLogger(__name__)


async def get_list(db: AsyncSession) -> Sequence[Source]:
    """Get list of sources"""
    return await paginate(db, select(Source).order_by(Source.created_at.desc()))


async def get(db: AsyncSession, source_id: UUID) -> Source:
    """Get source by id"""
    return await db.scalar(select(Source).filter(Source.id == source_id))


def parse_configuration(type: SourceType, source_configuration: dict) -> SourceConfiguration:
    """Parse configuration"""
    configuration: Optional[SourceConfiguration] = None

    match type:
        case SourceType.CONFLUENCE:
            configuration = ConfluenceConfiguration(**source_configuration)
        case SourceType.JIRA:
            configuration = JiraConfiguration(**source_configuration)

    return configuration


async def create(db: AsyncSession, title: str, description: Optional[str],
                 type: SourceType, configuration: Optional[SourceConfiguration]) -> Source:
    """Create source"""
    logger.debug("create, title=%s, description=%s, type=%s, configuration=%s",
                 title, description, type, configuration)

    source = Source(
        id=uuid.uuid4(),
        title=title,
        description=description,
        type=type,
        status=SourceStatus.NEW,
        created_by="admin",
        updated_by="admin",
        configuration=configuration.dict() if configuration is not None else None,
        progress=SourceProgress(id=uuid.uuid4())
    )

    db.add(source)
    await db.commit()
    await db.refresh(source)

    return source


async def upload(db: AsyncSession, source: Source, uploaded_file: UploadFile) -> Source:
    """Upload file"""
    return await save_file(db, source, uploaded_file)


async def update(db: AsyncSession, source: Source, title: str,
                 description: Optional[str], configuration: Optional[SourceConfiguration]) -> Source:
    """Update source"""
    source.title = title
    source.description = description
    source.updated_by = "admin"
    source.updated_at = datetime.now()
    source.configuration = configuration.dict() if configuration is not None else None

    db.add(source)
    await db.commit()
    await db.refresh(source)

    return source


async def delete(db: AsyncSession, source_id: UUID):
    """Delete source"""
    source = await get(db, source_id)

    if source is None:
        return

    await db.delete(source)
    await db.commit()


async def _set_status(db: AsyncSession, source: Source, status: SourceStatus, status_text: Optional[str] = None):
    """Set source status"""
    source.status = status
    source.status_text = status_text
    source.updated_by = "admin"
    source.updated_at = datetime.now()

    await db.commit()
    await db.refresh(source)

    return source


async def index(source_id: UUID, reindex: Optional[bool] = False):
    """Index source to vector storage"""
    logger.info("index, source_id=%s, rescan=%s", source_id, reindex)

    db: AsyncSession = await anext(get_db())
    source: Source = await get(db, source_id)

    if source is None:
        raise Exception("Source not found")

    try:
        if reindex:
            if not source.can_be_reindexed:
                raise Exception("Source cannot be reindexed")

        elif source.status != SourceStatus.NEW:
            raise Exception("Source cannot be indexed")

        source = await _set_status(db, source, SourceStatus.INDEXING)
        document_count: int = 0

        match source.type:
            case SourceType.UPLOAD:
                document_count = await index_upload(source)

        source.document_count = document_count
        del source.progress

        await _set_status(db, source, SourceStatus.FINISHED)

    except BaseException as error:
        logger.error("index, error: %s", error, exc_info=error)
        await _set_status(db, source, SourceStatus.ERROR, str(error))
        raise error

    finally:
        await db.close()
