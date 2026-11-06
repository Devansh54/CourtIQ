"""0001_initial_competitions: Categories and Competitions tables.

Revision ID: 0001_initial_competitions
Revises: None
Create Date: 2026-11-06 09:12:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0001_initial_competitions"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Categories Table
    op.create_table(
        "categories",
        sa.Column("category_id", sa.String(length=50), nullable=False),
        sa.Column("category_name", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint("category_id", name="pk_categories"),
    )

    # 2. Competitions Table
    op.create_table(
        "competitions",
        sa.Column("competition_id", sa.String(length=50), nullable=False),
        sa.Column("competition_name", sa.String(length=100), nullable=False),
        sa.Column("parent_id", sa.String(length=50), nullable=True),
        sa.Column("type", sa.String(length=20), nullable=False),
        sa.Column("gender", sa.String(length=10), nullable=False),
        sa.Column("category_id", sa.String(length=50), nullable=False),
        sa.ForeignKeyConstraint(
            ["category_id"],
            ["categories.category_id"],
            name="fk_competitions_category_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["parent_id"],
            ["competitions.competition_id"],
            name="fk_competitions_parent_id",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("competition_id", name="pk_competitions"),
    )

    # 3. Performance Indexes
    op.create_index(
        "idx_competitions_category_id",
        "competitions",
        ["category_id"],
        unique=False,
    )
    op.create_index(
        "idx_competitions_parent_id",
        "competitions",
        ["parent_id"],
        unique=False,
    )
    op.create_index(
        "idx_competitions_type",
        "competitions",
        ["type"],
        unique=False,
    )
    op.create_index(
        "idx_competitions_gender",
        "competitions",
        ["gender"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("idx_competitions_gender", table_name="competitions")
    op.drop_index("idx_competitions_type", table_name="competitions")
    op.drop_index("idx_competitions_parent_id", table_name="competitions")
    op.drop_index("idx_competitions_category_id", table_name="competitions")
    op.drop_table("competitions")
    op.drop_table("categories")
