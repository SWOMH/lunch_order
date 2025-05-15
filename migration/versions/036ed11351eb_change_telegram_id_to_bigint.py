"""change_telegram_id_to_bigint

Revision ID: 036ed11351eb
Revises: e6610a990c4f
Create Date: 2025-05-15 12:59:15.150880

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '036ed11351eb'
down_revision: Union[str, None] = 'e6610a990c4f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('users', 'telegram_id', type_=sa.BigInteger())
   

def downgrade() -> None:
    op.alter_column('users', 'telegram_id', type_=sa.Integer())
