"""created_admin_table

Revision ID: 8e0aa2915c57
Revises: 82bdb9f2bc52
Create Date: 2024-06-12 10:52:03.057857

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "8e0aa2915c57"
down_revision: Union[str, None] = "82bdb9f2bc52"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "admins",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column(
            "profile_picture_url",
            sa.String,
            default="/default_profile.jpg",
            nullable=False,
        ),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("email", sa.String, unique=True, index=True, nullable=False),
        sa.Column("phone_number", sa.String(20), nullable=False),
        sa.Column("password", sa.String, nullable=False),
        sa.Column("is_active", sa.Boolean, default=True),
        sa.Column("added_by", sa.String(50), nullable=False),
        sa.Column(
            "gender",
            sa.Enum("MALE", "FEMALE", "OTHER", name="gender_enum"),
            nullable=False,
        ),
        sa.Column(
            "permission",
            sa.Enum("SUPER_ADMIN", "ADMIN", name="admin_enum"),
            nullable=False,
        ),
        sa.Column("last_login", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            default=sa.text("now()"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("admins")
