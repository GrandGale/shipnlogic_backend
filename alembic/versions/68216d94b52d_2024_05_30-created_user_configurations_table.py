"""created_user_configurations_table

Revision ID: 68216d94b52d
Revises: 67e690c96c2a
Create Date: 2024-05-30 14:15:30.208563

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "68216d94b52d"
down_revision: Union[str, None] = "67e690c96c2a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user_configurations",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "user_id",
            sa.Integer,
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("notification_email", sa.Boolean, default=True),
        sa.Column("notification_inapp", sa.Boolean, default=True),
    )


def downgrade() -> None:
    op.drop_table("user_configurations")
