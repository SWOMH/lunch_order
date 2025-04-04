"""fix_enum_values

Revision ID: 59876add3844
Revises: 300a55ae4fb1
Create Date: 2025-04-04 19:14:38.698716

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '59876add3844'
down_revision: Union[str, None] = '300a55ae4fb1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
