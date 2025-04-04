"""fix_enum_values

Revision ID: 8ea81a5bb17f
Revises: 59876add3844
Create Date: 2025-04-04 19:15:17.608762

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8ea81a5bb17f'
down_revision: Union[str, None] = '59876add3844'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Создаем новый тип enum с правильными значениями
    op.execute("CREATE TYPE order_status_enum_new AS ENUM ('formalized', 'completed', 'canceled', 'deleted', 'unknown')")
    
    # Обновляем столбец order_status, используя временно NULL
    op.execute("ALTER TABLE public.orders ALTER COLUMN order_status DROP DEFAULT")
    op.execute("ALTER TABLE public.orders ALTER COLUMN order_status TYPE order_status_enum_new USING NULL")
    
    # Задаем значение по умолчанию 'formalized'
    op.execute("ALTER TABLE public.orders ALTER COLUMN order_status SET DEFAULT 'formalized'")
    
    # Обновляем существующие записи
    op.execute("UPDATE public.orders SET order_status = 'formalized' WHERE order_status IS NULL")
    
    # Удаляем старый тип enum
    op.execute("DROP TYPE order_status_enum")
    
    # Переименовываем новый тип enum
    op.execute("ALTER TYPE order_status_enum_new RENAME TO order_status_enum")


def downgrade() -> None:
    """Downgrade schema."""
    # Обратный процесс, если нужно вернуться назад
    op.execute("CREATE TYPE order_status_enum_old AS ENUM ('Оформлено', 'Выполнено', 'Отменено', 'Удалено', 'Неизвестно')")
    
    op.execute("ALTER TABLE public.orders ALTER COLUMN order_status DROP DEFAULT")
    op.execute("ALTER TABLE public.orders ALTER COLUMN order_status TYPE order_status_enum_old USING NULL")
    
    op.execute("ALTER TABLE public.orders ALTER COLUMN order_status SET DEFAULT 'Оформлено'")
    
    op.execute("UPDATE public.orders SET order_status = 'Оформлено' WHERE order_status IS NULL")
    
    op.execute("DROP TYPE order_status_enum")
    
    op.execute("ALTER TYPE order_status_enum_old RENAME TO order_status_enum")
