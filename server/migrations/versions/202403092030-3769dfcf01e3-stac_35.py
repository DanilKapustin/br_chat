"""STAC-35

Revision ID: 3769dfcf01e3
Revises: 3c5fa085e130
Create Date: 2024-03-09 20:30:41.937470

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3769dfcf01e3'
down_revision: Union[str, None] = '3c5fa085e130'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('message', sa.Column('user_id', sa.Uuid(), nullable=True))
    op.create_foreign_key(None, 'message', 'user', ['user_id'], ['id'])
    op.add_column('session', sa.Column('user_id', sa.Uuid(), nullable=True))
    op.create_foreign_key(None, 'session', 'user', ['user_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'session', type_='foreignkey')
    op.drop_column('session', 'user_id')
    op.drop_constraint(None, 'message', type_='foreignkey')
    op.drop_column('message', 'user_id')
    # ### end Alembic commands ###
