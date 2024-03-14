from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class ModelCreate(BaseModel):
    """Model create DTO"""

    name: str
    title: str
    description: Optional[str]
    configuration: dict[str, object]


class ModelUpdate(BaseModel):
    """Model update DTO"""

    id: UUID
    title: str
    description: Optional[str]
    configuration: dict[str, object]


class ModelResult(BaseModel):
    """Model result DTO"""

    id: UUID
    name: str
    title: str
    description: str
    is_system: bool
    configuration: Optional[dict]

    created_at: Optional[datetime] = datetime.now()
    updated_at: Optional[datetime] = datetime.now()
    created_by: Optional[str]
    updated_by: Optional[str]

    class Config:
        """Model result configuration"""

        orm_mode = True
