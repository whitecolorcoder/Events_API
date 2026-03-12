"""add first_name last_name to registration

Revision ID: 02ffaa4d8b32
Revises: bfd40d50ab89
Create Date: 2026-03-12 11:32:51.056485
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "02ffaa4d8b32"
down_revision: Union[str, None] = "bfd40d50ab89"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "registration",
        sa.Column("first_name", sa.String(length=100), nullable=False, server_default=""),
    )
    op.add_column(
        "registration",
        sa.Column("last_name", sa.String(length=100), nullable=False, server_default=""),
    )

    op.alter_column("registration", "first_name", server_default=None)
    op.alter_column("registration", "last_name", server_default=None)


def downgrade() -> None:
    op.drop_column("registration", "first_name")
    op.drop_column("registration", "last_name")
