"""Merge: JD migrations with SiteSettings migrations

Revision ID: 7160d1c6df3e
Revises: 819e23771ca9, eec0f985a050
Create Date: 2026-03-27 09:54:58.782093

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7160d1c6df3e'
down_revision: Union[str, Sequence[str], None] = ('819e23771ca9', 'eec0f985a050')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
