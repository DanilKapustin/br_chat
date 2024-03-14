from datetime import datetime
from enum import Enum
from uuid import UUID
from sqlalchemy.orm import Mapped, mapped_column
from .. import Base


class Config(str, Enum):
    """Configuration entry name"""
    LANGUAGE = "language"


class Language(Base):
    """Language configuration"""
    __tablename__ = "language"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(nullable=False)
    title: Mapped[str] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, default=datetime.utcnow)
    created_by: Mapped[str] = mapped_column(nullable=False)
    updated_by: Mapped[str] = mapped_column(nullable=False)

    def __repr__(self) -> str:
        return f"Language(id={self.id}, code={self.code}, title={self.title})"


class Configuration(Base):
    """Configuration"""
    __tablename__ = "configuration"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[Config] = mapped_column(nullable=False)
    value: Mapped[str] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, default=datetime.utcnow)
    created_by: Mapped[str] = mapped_column(nullable=False)
    updated_by: Mapped[str] = mapped_column(nullable=False)

    def __repr__(self) -> str:
        return f"Configuration(id={self.id}, name={self.name}, value={self.value})"
