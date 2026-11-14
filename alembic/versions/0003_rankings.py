
"""0003_rankings: Competitors and Rankings tables."""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# Revision identifiers
revision: str = "0003_rankings"
down_revision: Union[str, None] = "0002_venues"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create competitors and competitor_rankings tables."""

    op.create_table(
        "competitors",
        sa.Column("competitor_id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("country", sa.String(100), nullable=True),
        sa.Column("country_code", sa.String(10), nullable=True),
        sa.Column("abbreviation", sa.String(20), nullable=True),
    )

    op.create_table(
        "competitor_rankings",
        sa.Column("rank_id", sa.Integer(), primary_key=True),
        sa.Column("rank", sa.Integer(), nullable=False),
        sa.Column("movement", sa.Integer(), nullable=True),
        sa.Column("points", sa.Integer(), nullable=True),
        sa.Column("competitions_played", sa.Integer(), nullable=True),
        sa.Column(
            "competitor_id",
            sa.Integer(),
            sa.ForeignKey("competitors.competitor_id"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    """Drop rankings and competitors tables."""

    op.drop_table("competitor_rankings")
    op.drop_table("competitors")
