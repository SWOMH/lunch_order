from datetime import datetime
from sqlalchemy import select
from constant import CONSTANT
from database.models.lunch import Order, OrderItem
from database.telegram.core import DatabaseCore
from sqlalchemy.orm import selectinload


class Database(DatabaseCore):
    def __init__(self):
        super().__init__(str(CONSTANT.sync_url_connection))

        
    def get_today_orders_formatted(self) -> list[str]:
        """Получает заказы за сегодня и возвращает для Telegram"""
        with self.Session as session:
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            
            orders = session.execute(
                select(Order)
                .where(Order.datetime >= today_start)
                .options(
                    selectinload(Order.user),
                    selectinload(Order.order_items).selectinload(OrderItem.dish),
                    selectinload(Order.order_items).selectinload(OrderItem.variant)
                )
                .order_by(Order.datetime.desc())
            )
            orders = orders.scalars().all()
            
            formatted_orders = []
            for order in orders:
                order_text = f"Заказ #{order.id}\n"
                order_text += f"{order.user.full_name}\n"
                
                for item in order.order_items:
                    dish_name = item.dish.dish_name if item.dish else "Неизвестное блюдо"
                    if item.variant:
                        order_text += f"{dish_name} {item.variant.size}\n"
                    else:
                        order_text += f"{dish_name}\n"
                    if item.count > 1:
                        order_text += f" × {item.count}\n"
                
                order_text += f"Итого: {order.amount} руб.\n"
                order_text += "======================="
                
                formatted_orders.append(order_text)
        
            return formatted_orders