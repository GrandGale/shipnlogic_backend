"""created_user_password_reset_token_table

Revision ID: 7cdda97d045f
Revises: c5d0b8e1fb42
Create Date: 2024-06-05 08:16:35.237143

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7cdda97d045f"
down_revision: Union[str, None] = "c5d0b8e1fb42"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user_password_reset_tokens",
        sa.Column(
            "id", sa.Integer, primary_key=True, autoincrement=True, nullable=False
        ),
        sa.Column(
            "user_id",
            sa.Integer,
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("token", sa.String, unique=True),
        sa.Column("is_used", sa.Boolean, default=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("user_password_reset_tokens")
