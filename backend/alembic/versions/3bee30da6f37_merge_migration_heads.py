"""Merge migration heads

Revision ID: 3bee30da6f37
Revises: 67f6dbe2eece, f3a0cb9d02f7
Create Date: 2025-12-04 19:28:58.238321

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '3bee30da6f37'
down_revision = ('67f6dbe2eece', 'f3a0cb9d02f7')
branch_labels = None
depends_on = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
