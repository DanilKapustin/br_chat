"""message source

Revision ID: 02cf1afc4766
Revises: 56e7be42523f
Create Date: 2024-03-09 11:54:55.400115

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '02cf1afc4766'
down_revision: Union[str, None] = '56e7be42523f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('message_source',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('message_id', sa.Uuid(), nullable=False),
    sa.Column('source_id', sa.Uuid(), nullable=True),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('url', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['message_id'], ['message.id'], ),
    sa.ForeignKeyConstraint(['source_id'], ['source.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('message_source')
    # ### end Alembic commands ###