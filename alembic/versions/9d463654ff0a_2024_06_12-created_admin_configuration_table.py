"""created_admin_configuration_table

Revision ID: 9d463654ff0a
Revises: 8e0aa2915c57
Create Date: 2024-06-12 17:44:07.826567

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "9d463654ff0a"
down_revision: Union[str, None] = "8e0aa2915c57"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "admin_configurations",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "admin_id",
            sa.Integer,
            sa.ForeignKey("admins.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("notification_email", sa.Boolean, default=True),
        sa.Column("notification_inapp", sa.Boolean, default=True),
    )


def downgrade() -> None:
    op.drop_table("admin_configurations")
