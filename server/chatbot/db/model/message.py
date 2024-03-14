from datetime import datetime
from typing import List
from uuid import UUID
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .. import Base
from .user import User


class Message(Base):
    """Message model"""

    __tablename__ = "message"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    session_id: Mapped[UUID] = mapped_column(ForeignKey("session.id"))

    is_system: Mapped[bool] = mapped_column(nullable=False)
    message: Mapped[str] = mapped_column(nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        nullable=False, default=datetime.utcnow
    )
    created_by: Mapped[str] = mapped_column(nullable=False)

    sources: Mapped[List["MessageSource"]] = relationship(
        cascade="all, delete-orphan", lazy="joined"
    )
    rating: Mapped[int] = mapped_column(nullable=True)
    is_hidden: Mapped[bool] = mapped_column(
        nullable=False, default=False, server_default="0"
    )

    user_id: Mapped[UUID] = mapped_column(ForeignKey("user.id"), nullable=True)
    user: Mapped[User] = relationship(lazy="joined")


class MessageSource(Base):
    """Message source model"""

    __tablename__ = "message_source"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    message_id: Mapped[UUID] = mapped_column(ForeignKey("message.id"))
    source_id: Mapped[UUID] = mapped_column(nullable=True)
    source_title: Mapped[str] = mapped_column(nullable=True)

    title: Mapped[str] = mapped_column(nullable=False)
    subtitle: Mapped[str] = mapped_column(nullable=True)
    url: Mapped[str] = mapped_column(nullable=True)

    chunk: Mapped[int] = mapped_column(nullable=True)
    total_chunks: Mapped[int] = mapped_column(nullable=True)

    message: Mapped[Message] = relationship("Message", back_populates="sources")
