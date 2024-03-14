"""tool max tokens

Revision ID: d7f7168dca46
Revises: 9406d0039ba7
Create Date: 2024-03-09 17:32:43.989579

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d7f7168dca46"
down_revision: Union[str, None] = "9406d0039ba7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute(
        "UPDATE tool SET configuration = configuration || hstore('max_tokens', '1000')"
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute("UPDATE tool SET configuration = delete(configuration, 'max_tokens')")
    # ### end Alembic commands ###
