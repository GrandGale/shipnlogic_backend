"""created_admin_notification_table

Revision ID: 8e64e7d2b259
Revises: 9d463654ff0a
Create Date: 2024-06-12 17:50:32.335699

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "8e64e7d2b259"
down_revision: Union[str, None] = "9d463654ff0a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "admin_notifications",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "admin_id",
            sa.Integer,
            sa.ForeignKey("admins.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("content", sa.String(255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("is_read", sa.Boolean, default=False),
    )


def downgrade() -> None:
    op.drop_table("admin_notifications")
