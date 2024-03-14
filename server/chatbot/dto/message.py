from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class MessageSource(BaseModel):
    """Message source model"""

    id: UUID
    source_id: Optional[UUID]
    source_title: Optional[str]
    title: str
    subtitle: Optional[str]
    url: Optional[str]
    chunk: Optional[int]
    total_chunks: Optional[int]

    class Config:
        """Message source configuration"""

        orm_mode = True


class MessageResult(BaseModel):
    """Message result model"""

    id: UUID

    session_id: UUID
    is_system: bool
    message: str

    created_at: Optional[datetime] = datetime.now()
    created_by: Optional[str]

    sources: list[MessageSource]
    rating: Optional[int] = 0
    is_hidden: bool

    class Config:
        """Message result configuration"""

        orm_mode = True
