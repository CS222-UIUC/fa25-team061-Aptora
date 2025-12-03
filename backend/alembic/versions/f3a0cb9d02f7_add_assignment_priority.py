"""add priority column to assignments

Revision ID: f3a0cb9d02f7
Revises: 45d42227d875
Create Date: 2025-11-13 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "f3a0cb9d02f7"
down_revision = "45d42227d875"
branch_labels = None
depends_on = None


priority_enum = sa.Enum("high", "medium", "low", name="prioritylevel")


def upgrade() -> None:
    bind = op.get_bind()
    priority_enum.create(bind, checkfirst=True)

    op.add_column(
        "assignments",
        sa.Column(
            "priority",
            priority_enum,
            nullable=False,
            server_default="medium",
        ),
    )
    op.execute("UPDATE assignments SET priority='medium' WHERE priority IS NULL")
    op.alter_column("assignments", "priority", server_default=None)


def downgrade() -> None:
    op.drop_column("assignments", "priority")
    bind = op.get_bind()
    priority_enum.drop(bind, checkfirst=True)

