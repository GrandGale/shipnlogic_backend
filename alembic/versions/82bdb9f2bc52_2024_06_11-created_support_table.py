"""created_support_table

Revision ID: 82bdb9f2bc52
Revises: 9965c6e1d607
Create Date: 2024-06-11 17:18:20.887752

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "82bdb9f2bc52"
down_revision: Union[str, None] = "9965c6e1d607"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "support",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("full_name", sa.String(50), nullable=False),
        sa.Column("email", sa.String, unique=True, nullable=False),
        sa.Column("category", sa.String, nullable=False),
        sa.Column("upload_file_url", sa.String, nullable=True),
        sa.Column("description", sa.String, nullable=False),
        sa.Column("is_resolved", sa.Boolean, default=False, nullable=False),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE")),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("support")
