from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class SessionCreate(BaseModel):
    """Session create"""

    title: str
    tool_id: UUID


class SessionResult(SessionCreate):
    """Session result"""

    id: UUID

    created_at: Optional[datetime] = datetime.now()
    created_by: Optional[str]

    class Config:
        """Session result configuration"""

        orm_mode = True


class MessageErrorResult(BaseModel):
    """Message error result model"""

    is_system: bool = True
    is_error: bool = True
    created_at: Optional[datetime] = datetime.now()
    created_by: Optional[str]

    message: str
