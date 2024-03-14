from datetime import datetime
from typing import List
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .. import Base
from .message import Message
from .user import User


class Session(Base):
    """Session model"""

    __tablename__ = "session"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    tool_id: Mapped[UUID] = mapped_column(ForeignKey("tool.id"))
    title: Mapped[str] = mapped_column(nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        nullable=False, default=datetime.utcnow
    )
    created_by: Mapped[str] = mapped_column(nullable=False)

    messages: Mapped[List["Message"]] = relationship(
        cascade="all, delete-orphan", lazy="select"
    )

    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"), nullable=True)
    user: Mapped[User] = relationship(lazy="joined")

    def __repr__(self) -> str:
        return f"<Session(id={self.id}, title={self.title})>"
