
"""0002_venues: Complexes and Venues tables."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# Revision identifiers
revision: str = "0002_venues"
down_revision: Union[str, None] = "0001_initial_competitions"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create complexes and venues tables."""

    # 1. Complexes table
    op.create_table(
        "complexes",
        sa.Column("complex_id", sa.String(length=50), nullable=False),
        sa.Column("complex_name", sa.String(length=100), nullable=False),
        sa.PrimaryKeyConstraint(
            "complex_id",
            name="pk_complexes",
        ),
    )

    # 2. Venues table
    op.create_table(
        "venues",
        sa.Column("venue_id", sa.String(length=50), nullable=False),
        sa.Column("venue_name", sa.String(length=100), nullable=False),
        sa.Column("city_name", sa.String(length=100), nullable=False),
        sa.Column("country_name", sa.String(length=100), nullable=False),
        sa.Column("country_code", sa.CHAR(length=3), nullable=False),
        sa.Column("timezone", sa.String(length=100), nullable=False),
        sa.Column("complex_id", sa.String(length=50), nullable=False),

        sa.ForeignKeyConstraint(
            ["complex_id"],
            ["complexes.complex_id"],
            name="fk_venues_complex_id",
            ondelete="CASCADE",
        ),

        sa.PrimaryKeyConstraint(
            "venue_id",
            name="pk_venues",
        ),
    )

    # 3. Performance indexes
    op.create_index(
        "idx_venues_complex_id",
        "venues",
        ["complex_id"],
        unique=False,
    )

    op.create_index(
        "idx_venues_country_code",
        "venues",
        ["country_code"],
        unique=False,
    )

    op.create_index(
        "idx_venues_city_name",
        "venues",
        ["city_name"],
        unique=False,
    )


def downgrade() -> None:
    """Remove venues and complexes tables."""

    op.drop_index(
        "idx_venues_city_name",
        table_name="venues",
    )

    op.drop_index(
        "idx_venues_country_code",
        table_name="venues",
    )

    op.drop_index(
        "idx_venues_complex_id",
        table_name="venues",
    )

    op.drop_table("venues")
    op.drop_table("complexes")
