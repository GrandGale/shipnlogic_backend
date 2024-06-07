"""created_company_table

Revision ID: 9965c6e1d607
Revises: f3eb3f84334b
Create Date: 2024-06-06 10:06:35.875369

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9965c6e1d607'
down_revision: Union[str, None] = 'f3eb3f84334b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "companies",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String, nullable=False),
        sa.Column("registration_number", sa.String, unique=True, nullable=False),
        sa.Column("email", sa.String, unique=True, nullable=False),
        sa.Column("phone", sa.String, unique=True, nullable=False),
        sa.Column("address", sa.String, nullable=False),
        sa.Column("tax_identification_number", sa.String, unique=True, nullable=False),
        sa.Column("license_image_url", sa.String, server_default="/default_license.jpg",nullable=False),
        sa.Column("permit_image_url", sa.String, server_default="/default_permit.jpg",nullable=False),
        sa.Column("is_verified", sa.Boolean, default=False),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("companies")
