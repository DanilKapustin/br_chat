from datetime import datetime
from uuid import UUID

from sqlalchemy import ForeignKey
from sqlalchemy.dialects.postgresql import HSTORE
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import Mapped, mapped_column

from .. import Base


class Tool(Base):
    """Tool"""

    __tablename__ = "tool"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    title: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=True)
    is_system: Mapped[bool] = mapped_column(nullable=False)
    configuration: Mapped[dict] = mapped_column(
        MutableDict.as_mutable(HSTORE), nullable=True
    )
    model_id: Mapped[UUID] = mapped_column(ForeignKey("model.id"))

    created_at: Mapped[datetime] = mapped_column(
        nullable=False, default=datetime.utcnow
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, default=datetime.utcnow
    )
    created_by: Mapped[str] = mapped_column(nullable=False)
    updated_by: Mapped[str] = mapped_column(nullable=False)

    def __repr__(self) -> str:
        return f"Tool(id={self.id}, name={self.name}, title={self.title})"
