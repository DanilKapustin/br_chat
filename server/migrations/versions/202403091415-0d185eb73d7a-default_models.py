"""default models

Revision ID: 0d185eb73d7a
Revises: d80d51462a2d
Create Date: 2024-03-09 14:15:44.546176

"""
from typing import Sequence, Union
from datetime import datetime
from uuid import UUID

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "0d185eb73d7a"
down_revision: Union[str, None] = "d80d51462a2d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

model_table = sa.table(
    "model",
    sa.column("id", sa.UUID),
    sa.column("name", sa.String),
    sa.column("title", sa.String),
    sa.column("description", sa.String),
    sa.column("is_system", sa.Boolean),
    sa.column("configuration", postgresql.HSTORE(text_type=sa.Text())),
    sa.column("created_at", sa.DateTime),
    sa.column("updated_at", sa.DateTime),
    sa.column("created_by", sa.String),
    sa.column("updated_by", sa.String),
)


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    now = datetime.now()
    op.bulk_insert(
        model_table,
        [
            {
                "id": UUID("d9216f23-1f33-4ce1-9b5e-24f16513becc"),
                "name": "llama2",
                "title": "Llama-2 13B Chat (8 bit)",
                "description": "Llama-2 chat model, 13 billion params, 8 bit quantization",
                "is_system": True,
                "configuration": {
                    "path": "/media/love/ml/Llama-2-13B-chat-GGUF/llama-2-13b-chat.Q8_0.gguf",
                    "context_length": "4096",
                    "top_k": "30",
                    "top_p": "0.9",
                    "repeat_penalty": "1.2",
                    "temperature": "1.0",
                },
                "created_at": now,
                "updated_at": now,
                "created_by": "system",
                "updated_by": "system",
            },
            {
                "id": UUID("fe98136f-286f-4344-80c7-82ff7d3b08b5"),
                "name": "saiga2",
                "title": "Saiga-2 13B Chat (8 bit)",
                "description": "Saiga-2 chat model, 13 billion params, 8 bit quantization. Based on Llama-2 13B.",
                "is_system": True,
                "configuration": {
                    "path": "/media/love/ml/saiga2_13b_gguf/model-q8_0.gguf",
                    "context_length": "4096",
                    "top_k": "30",
                    "top_p": "0.9",
                    "repeat_penalty": "1.2",
                    "temperature": "1.0",
                },
                "created_at": now,
                "updated_at": now,
                "created_by": "system",
                "updated_by": "system",
            },
        ],
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute("DELETE FROM model WHERE is_system")
    # ### end Alembic commands ###
