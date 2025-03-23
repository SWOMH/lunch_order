from fastapi import HTTPException
from database.main_connect import DataBaseMainConnect
from database.models.lunch import Dish, User, Order, OrderItem



class DatabaseOrder(DataBaseMainConnect):

    def ordering_food(self, foods: list[int], telegram_id: int):
        session = self.Session()
        with session.no_autoflush:
            dishes = session.query(Dish).filter(Dish.id.in_(foods)).all()
            if not dishes or len(dishes) != len(foods):
                raise HTTPException(status_code=400, detail="Некоторые блюда не найдены")
            user = session.query(User).filter_by(telegram_id=telegram_id).first()
            new_order = Order(
                user_id=user.id
            )
            session.add(new_order)
            session.flush()
            order_items = []
            for dish_id in foods:
                order_items.append(OrderItem(order_id=new_order.id, dish_id=dish_id))
            session.bulk_save_objects(order_items)
            session.commit()
            return HTTPException(status_code=200, detail="Заказ добавлен")
