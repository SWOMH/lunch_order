"""change_iiko_id_to_bigint

Revision ID: 28981c26ff5d
Revises: 036ed11351eb
Create Date: 2025-05-16 14:58:59.118504

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '28981c26ff5d'
down_revision: Union[str, None] = '036ed11351eb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('dish', 'id_iiko', type_=sa.BigInteger())
    op.alter_column('dish_variants', 'id_iiko', type_=sa.BigInteger())


def downgrade() -> None:
    op.alter_column('dish', 'id_iiko', type_=sa.Integer())
    op.alter_column('dish_variants', 'id_iiko', type_=sa.Integer())
