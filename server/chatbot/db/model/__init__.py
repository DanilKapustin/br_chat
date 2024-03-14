from sqlalchemy import Table

from .configuration import Configuration, Config
from .message import Message, MessageSource
from .model import Model
from .session import Session
from .source import Source, SourceType, SourceProgress, SourceStatus
from .tool import Tool
from .user import User
from .. import Base

__all__ = [
    "Message",
    "MessageSource",
    "Session",
    "Source",
    "SourceType",
    "SourceProgress",
    "SourceStatus",
    "Configuration",
    "Config",
    "Model",
    "Tool",
    "User",
    "clone_model",
]


def clone_model(
    model_: Base, exclude: tuple[str] = ("created_at", "updated_at")
) -> dict:
    """Clone an arbitrary sqlalchemy model object without its primary key values."""
    table: Table = model_.__table__

    clone_fields: list[str] = [
        k
        for k in table.columns.keys()
        if k not in table.primary_key and k not in exclude
    ]

    data: dict = {c: getattr(model_, c) for c in clone_fields}

    return data
