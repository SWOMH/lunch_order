"""change_iiko_id_to_numeric

Revision ID: 7cf670ef284b
Revises: 28981c26ff5d
Create Date: 2025-05-16 15:17:07.202943

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7cf670ef284b'
down_revision: Union[str, None] = '28981c26ff5d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('dish', 'id_iiko',
                   existing_type=sa.BIGINT(),
                   type_=sa.Numeric(precision=38, scale=0),
                   postgresql_using='id_iiko::numeric(38,0)')
    
    op.alter_column('dish_variants', 'id_iiko',
                   existing_type=sa.BIGINT(),
                   type_=sa.Numeric(precision=38, scale=0),
                   postgresql_using='id_iiko::numeric(38,0)')


def downgrade() -> None:
    op.alter_column('dish', 'id_iiko',
                   existing_type=sa.Numeric(precision=38, scale=0),
                   type_=sa.BIGINT(),
                   postgresql_using='id_iiko::bigint')
    
    op.alter_column('dish_variants', 'id_iiko',
                   existing_type=sa.Numeric(precision=38, scale=0),
                   type_=sa.BIGINT(),
                   postgresql_using='id_iiko::bigint')
