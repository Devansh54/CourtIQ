"""Add performance indexes for Rankings domain."""

from typing import Sequence, Union

from alembic import op


revision: str = "2a4b6c8d9e10"
down_revision: Union[str, None] = "1c3add79e37f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create indexes for Rankings queries."""

    op.create_index(
        "idx_rankings_competitor_id",
        "competitor_rankings",
        ["competitor_id"],
        unique=False,
    )

    op.create_index(
        "idx_rankings_rank",
        "competitor_rankings",
        ["rank"],
        unique=False,
    )

    op.create_index(
        "idx_competitors_country_code",
        "competitors",
        ["country_code"],
        unique=False,
    )


def downgrade() -> None:
    """Remove Rankings indexes."""

    op.drop_index(
        "idx_competitors_country_code",
        table_name="competitors",
    )

    op.drop_index(
        "idx_rankings_rank",
        table_name="competitor_rankings",
    )

    op.drop_index(
        "idx_rankings_competitor_id",
        table_name="competitor_rankings",
    )