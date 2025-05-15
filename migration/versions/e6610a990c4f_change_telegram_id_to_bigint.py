"""change_telegram_id_to_bigint

Revision ID: e6610a990c4f
Revises: 70e4dc66c61f
Create Date: 2025-05-15 12:57:42.656751

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e6610a990c4f'
down_revision: Union[str, None] = '70e4dc66c61f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
