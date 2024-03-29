"""max results for source analysis

Revision ID: d01cbd6dfbd8
Revises: d323a2eea125
Create Date: 2024-03-09 15:52:51.446640

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d01cbd6dfbd8"
down_revision: Union[str, None] = "d323a2eea125"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute(
        "UPDATE tool SET configuration = configuration || hstore('max_results', '10') WHERE name = 'source_analysis'"
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute(
        "UPDATE tool SET configuration = delete(configuration, 'max_results') WHERE name = 'source_analysis'"
    )
    # ### end Alembic commands ###
