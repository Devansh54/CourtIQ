
"""Align rankings IDs with schemas."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "1c3add79e37f"
down_revision: Union[str, None] = "0003_rankings"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Change competitor IDs from Integer to String."""

    # Remove the foreign key before changing column types.
    op.drop_constraint(
        "competitor_rankings_competitor_id_fkey",
        "competitor_rankings",
        type_="foreignkey",
    )

    # Change the competitor primary key to String.
    op.alter_column(
        "competitors",
        "competitor_id",
        existing_type=sa.Integer(),
        type_=sa.String(length=50),
        existing_nullable=False,
        postgresql_using="competitor_id::varchar(50)",
    )

    # Change the matching foreign key column to String.
    op.alter_column(
        "competitor_rankings",
        "competitor_id",
        existing_type=sa.Integer(),
        type_=sa.String(length=50),
        existing_nullable=False,
        postgresql_using="competitor_id::varchar(50)",
    )

    # Recreate the foreign key.
    op.create_foreign_key(
        "competitor_rankings_competitor_id_fkey",
        "competitor_rankings",
        "competitors",
        ["competitor_id"],
        ["competitor_id"],
    )


def downgrade() -> None:
    """Restore competitor IDs to Integer."""

    op.drop_constraint(
        "competitor_rankings_competitor_id_fkey",
        "competitor_rankings",
        type_="foreignkey",
    )

    op.alter_column(
        "competitors",
        "competitor_id",
        existing_type=sa.String(length=50),
        type_=sa.Integer(),
        existing_nullable=False,
        postgresql_using="competitor_id::integer",
    )

    op.alter_column(
        "competitor_rankings",
        "competitor_id",
        existing_type=sa.String(length=50),
        type_=sa.Integer(),
        existing_nullable=False,
        postgresql_using="competitor_id::integer",
    )

    op.create_foreign_key(
        "competitor_rankings_competitor_id_fkey",
        "competitor_rankings",
        "competitors",
        ["competitor_id"],
        ["competitor_id"],
    )
