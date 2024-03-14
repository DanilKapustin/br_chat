from datetime import datetime
from enum import Enum
from uuid import UUID
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import HSTORE
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.ext.hybrid import hybrid_property
from .. import Base


class SourceType(str, Enum):
    """Source type enum"""
    UPLOAD = "UPLOAD"
    CONFLUENCE = "CONFLUENCE"
    JIRA = "JIRA"


class SourceStatus(str, Enum):
    """Source status enum"""
    NEW = "NEW"
    INDEXING = "INDEXING"
    FINISHED = "FINISHED"
    ERROR = "ERROR"


class Source(Base):
    __tablename__ = "source"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    type: Mapped[SourceType] = mapped_column(nullable=False)
    document_count: Mapped[int] = mapped_column(nullable=False, default=0)
    configuration: Mapped[dict] = mapped_column(
        MutableDict.as_mutable(HSTORE), nullable=True)
    status: Mapped[SourceStatus] = mapped_column(nullable=False)
    status_text: Mapped[str] = mapped_column(nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, default=datetime.utcnow)
    created_by: Mapped[str] = mapped_column(nullable=False)
    updated_by: Mapped[str] = mapped_column(nullable=False)

    progress: Mapped["SourceProgress"] = relationship(back_populates="source",
                                                      cascade="all, delete-orphan",
                                                      lazy="joined")

    @hybrid_property
    def can_be_reindexed(self) -> bool:
        """Check if source can be reindexed"""
        return self.type != SourceType.UPLOAD and self.status in (
            SourceStatus.FINISHED, SourceStatus.ERROR, SourceStatus.NEW)

    def __repr__(self) -> str:
        return f"Source(id={self.id}, title={self.title}, type={self.type})"


class SourceProgress(Base):
    __tablename__ = "source_progress"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    source_id: Mapped[UUID] = mapped_column(
        ForeignKey("source.id"), unique=True)
    progress: Mapped[float] = mapped_column(nullable=False, default=0.0)
    document_count: Mapped[int] = mapped_column(nullable=False, default=0)
    indexed_count: Mapped[int] = mapped_column(nullable=False, default=0)
    temporary_file_path: Mapped[str] = mapped_column(nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    source: Mapped["Source"] = relationship(back_populates="progress")
