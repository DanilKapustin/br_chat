from uuid import UUID

from sqlalchemy.orm import Mapped, mapped_column
from .. import Base


class User(Base):
    __tablename__ = "user"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(nullable=False)
    hashed_password: Mapped[str] = mapped_column(nullable=False)
