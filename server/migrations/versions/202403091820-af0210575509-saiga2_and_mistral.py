"""saiga2 and mistral

Revision ID: af0210575509
Revises: f3b649bf4dcd
Create Date: 2024-03-09 18:20:34.947154

"""
from datetime import datetime
from typing import Sequence, Union
from uuid import UUID

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "af0210575509"
down_revision: Union[str, None] = "f3b649bf4dcd"
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
    op.execute("UPDATE model SET configuration = configuration || hstore('path', '')")

    op.execute(
        "UPDATE model SET name = 'llamacpp', configuration = configuration || hstore('chat_format', 'llama2') WHERE name = 'llama2'"
    )

    op.execute(
        "UPDATE model SET title = 'Mistral 7B Saiga-2', "
        + "description = 'Чат-модель Mistral v0.1, дообученная на датасете Saiga-2, 7 миллиардов параметров, 8-битовая квантизация' "
        + "WHERE id = 'fe98136f-286f-4344-80c7-82ff7d3b08b5'"
    )

    now = datetime.now()
    op.bulk_insert(
        model_table,
        [
            {
                "id": UUID("02eb94a9-cffa-4096-879f-b3a673251c59"),
                "name": "llamacpp",
                "title": "Mistral 7B OpenOrca",
                "description": "Mistral v0.1 chat model fine-tuned on OpenOrca dataset, 7 billion params, 8 bit quantization",
                "is_system": True,
                "configuration": {
                    "path": "",
                    "context_length": "4096",
                    "top_k": "30",
                    "top_p": "1.0",
                    "repeat_penalty": "1.1",
                    "temperature": "1.1",
                    "prompt_system": "You are an AI assistant. You are helpful, clever, focused on the topic. You provide detailed and direct answers.",
                    "chat_format": "chatml",
                    "threads": "4",
                    "gpu_layers": "1000",
                },
                "created_at": now,
                "updated_at": now,
                "created_by": "system",
                "updated_by": "system",
            },
        ],
    )

    op.execute(
        "UPDATE tool SET model_id = '02eb94a9-cffa-4096-879f-b3a673251c59' WHERE id = 'd0a6eaa2-05ea-4fe7-9550-897027405c46'"
    )
    op.execute(
        "UPDATE tool SET model_id = '02eb94a9-cffa-4096-879f-b3a673251c59' WHERE id = 'bd05ba50-6671-414d-a925-264a1246973f'"
    )
    op.execute(
        "UPDATE model SET configuration = configuration || hstore('threads', '4') WHERE name IN ('llamacpp', 'saiga2') AND NOT configuration ? 'threads'"
    )
    op.execute(
        "UPDATE model SET configuration = configuration || hstore('gpu_layers', '1000') WHERE name IN ('llamacpp', 'saiga2') AND NOT configuration ? 'gpu_layers'"
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute(
        "UPDATE model SET name = 'llama2', configuration = delete(configuration, 'chat_format') WHERE name = 'llamacpp'"
    )
    op.execute(
        "UPDATE tool SET model_id = 'd9216f23-1f33-4ce1-9b5e-24f16513becc' WHERE id = 'd0a6eaa2-05ea-4fe7-9550-897027405c46'"
    )
    op.execute(
        "UPDATE tool SET model_id = 'd9216f23-1f33-4ce1-9b5e-24f16513becc' WHERE id = 'bd05ba50-6671-414d-a925-264a1246973f'"
    )

    op.execute("DELETE FROM model WHERE id = '02eb94a9-cffa-4096-879f-b3a673251c59'")
    # ### end Alembic commands ###