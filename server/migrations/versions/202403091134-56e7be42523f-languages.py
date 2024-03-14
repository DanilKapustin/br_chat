"""languages

Revision ID: 56e7be42523f
Revises: c2bc7954e55f
Create Date: 2024-03-09 11:34:44.807843

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from uuid import UUID
from datetime import datetime


# revision identifiers, used by Alembic.
revision: str = '56e7be42523f'
down_revision: Union[str, None] = 'c2bc7954e55f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

language_table = sa.table(
    "language",
    sa.column("id", sa.UUID),
    sa.column("code", sa.String),
    sa.column("title", sa.String),
    sa.column("created_at", sa.DateTime),
    sa.column("updated_at", sa.DateTime),
    sa.column("created_by", sa.String),
    sa.column("updated_by", sa.String))


def upgrade() -> None:
    now = datetime.now()
    op.bulk_insert(language_table, [
        {"id": UUID("b75da92e-5f0d-40d4-95ed-2a336d91cb9b"), "code": "en", "title": "English", "created_at": now,
            "updated_at": now, "created_by": "system", "updated_by": "system"},
        {"id": UUID("b75da92e-5f0d-40d4-95ed-2a336d91cb9c"), "code": "ru", "title": "Русский", "created_at": now,
            "updated_at": now, "created_by": "system", "updated_by": "system"},
    ])


def downgrade() -> None:
    op.execute("DELETE FROM language")
