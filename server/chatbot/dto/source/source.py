from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel
from chatbot.db.model import SourceStatus, SourceType


class SourceCreate(BaseModel):
    """Source create"""
    title: str
    description: Optional[str]
    type: Optional[SourceType] = SourceType.UPLOAD
    configuration: Optional[dict]


class SourceUpdate(BaseModel):
    """Source update"""
    id: UUID
    title: str
    description: Optional[str]
    configuration: Optional[dict]


class SourceProgressResult(BaseModel):
    """Source progress"""
    document_count: int = 0
    indexed_count: int = 0
    progress: float = 0.0

    class Config:
        """Source progress configuration"""
        orm_mode = True


class SourceResult(SourceCreate):
    """Source result"""
    id: UUID

    document_count: Optional[int] = 0
    status: Optional[SourceStatus] = SourceStatus.NEW
    status_text: Optional[str]
    progress: Optional[SourceProgressResult]

    created_at: Optional[datetime] = datetime.now()
    updated_at: Optional[datetime] = datetime.now()
    created_by: Optional[str]
    updated_by: Optional[str]

    class Config:
        """Source result configuration"""
        orm_mode = True
