from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class ToolCreate(BaseModel):
    """Tool create DTO"""

    name: str
    title: str
    description: Optional[str]
    configuration: dict[str, object]
    model_id: UUID


class ToolUpdate(BaseModel):
    """Tool update DTO"""

    id: UUID
    title: str
    description: Optional[str]
    configuration: dict[str, object]
    model_id: UUID


class ToolResult(BaseModel):
    """Tool result DTO"""

    id: UUID
    name: str
    title: str
    description: Optional[str]
    is_system: bool
    configuration: dict[str, object]
    model_id: UUID

    created_at: Optional[datetime] = datetime.now()
    updated_at: Optional[datetime] = datetime.now()
    created_by: Optional[str]
    updated_by: Optional[str]

    class Config:
        """Tool result configuration"""

        orm_mode = True
