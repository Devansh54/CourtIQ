
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

    dialect = op.get_bind().dialect.name

    if dialect == "sqlite":
        # SQLite requires batch mode to modify foreign keys and columns.
        naming_convention = {
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s"
        }

        # First remove the existing foreign key and change its column.
        # The original SQLite foreign key is unnamed, so batch mode
        # applies the naming convention above.
        with op.batch_alter_table(
            "competitor_rankings",
            recreate="always",
            naming_convention=naming_convention,
        ) as batch_op:
            batch_op.drop_constraint(
                "fk_competitor_rankings_competitor_id_competitors",
                type_="foreignkey",
            )
            batch_op.alter_column(
                "competitor_id",
                existing_type=sa.Integer(),
                type_=sa.String(length=50),
                existing_nullable=False,
            )

        # Change the competitor primary key.
        with op.batch_alter_table(
            "competitors",
            recreate="always",
        ) as batch_op:
            batch_op.alter_column(
                "competitor_id",
                existing_type=sa.Integer(),
                type_=sa.String(length=50),
                existing_nullable=False,
            )

        # Recreate the foreign key after both columns have matching types.
        with op.batch_alter_table(
            "competitor_rankings",
            recreate="always",
        ) as batch_op:
            batch_op.create_foreign_key(
                "competitor_rankings_competitor_id_fkey",
                "competitors",
                ["competitor_id"],
                ["competitor_id"],
            )

    else:
        # PostgreSQL supports direct constraint and column alterations.
        op.drop_constraint(
            "competitor_rankings_competitor_id_fkey",
            "competitor_rankings",
            type_="foreignkey",
        )

        op.alter_column(
            "competitors",
            "competitor_id",
            existing_type=sa.Integer(),
            type_=sa.String(length=50),
            existing_nullable=False,
            postgresql_using="competitor_id::varchar(50)",
        )

        op.alter_column(
            "competitor_rankings",
            "competitor_id",
            existing_type=sa.Integer(),
            type_=sa.String(length=50),
            existing_nullable=False,
            postgresql_using="competitor_id::varchar(50)",
        )

        op.create_foreign_key(
            "competitor_rankings_competitor_id_fkey",
            "competitor_rankings",
            "competitors",
            ["competitor_id"],
            ["competitor_id"],
        )


def downgrade() -> None:
    """Restore competitor IDs to Integer."""

    dialect = op.get_bind().dialect.name

    if dialect == "sqlite":
        naming_convention = {
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s"
        }

        # Remove the foreign key before changing either column.
        with op.batch_alter_table(
            "competitor_rankings",
            recreate="always",
            naming_convention=naming_convention,
        ) as batch_op:
            batch_op.drop_constraint(
                "competitor_rankings_competitor_id_fkey",
                type_="foreignkey",
            )
            batch_op.alter_column(
                "competitor_id",
                existing_type=sa.String(length=50),
                type_=sa.Integer(),
                existing_nullable=False,
            )

        with op.batch_alter_table(
            "competitors",
            recreate="always",
        ) as batch_op:
            batch_op.alter_column(
                "competitor_id",
                existing_type=sa.String(length=50),
                type_=sa.Integer(),
                existing_nullable=False,
            )

        with op.batch_alter_table(
            "competitor_rankings",
            recreate="always",
        ) as batch_op:
            batch_op.create_foreign_key(
                "competitor_rankings_competitor_id_fkey",
                "competitors",
                ["competitor_id"],
                ["competitor_id"],
            )

    else:
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
