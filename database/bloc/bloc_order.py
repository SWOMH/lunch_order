from fastapi import HTTPException
from sqlalchemy import select
from custom_types import OrderType
from database.decorators import connection
from database.main_connect import DataBaseMainConnect
from database.models.lunch import Dish, User, Order, OrderItem
from sqlalchemy.ext.asyncio import AsyncSession



class DatabaseOrder(DataBaseMainConnect):

    @connection
    async def ordering_food(self, order: OrderType, session: AsyncSession):
        user = await session.scalar(
            select(User).where(User.telegram_id == order.telegram_id))
        
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        if user.banned:
            raise HTTPException(
                status_code=403,
                detail="Заказ недоступен: пользователь заблокирован"
            )

        dish_ids = [dish.dish_id for dish in order.dishes]
        dishes = await session.scalars(
            select(Dish).where(Dish.id.in_(dish_ids)))
        dishes = dishes.all()

        if len(dishes) != len(dish_ids):
            found_ids = {dish.id for dish in dishes}
            not_found = [id_ for id_ in dish_ids if id_ not in found_ids]
            raise HTTPException(
                status_code=400,
                detail=f"Некоторые блюда не найдены: {not_found}"
            )
        
        new_order = Order(user_id=user.id, amount=order.amount)
        session.add(new_order)
        await session.flush()

        order_items = [
            OrderItem(
                order_id=new_order.id,
                dish_id=item.dish_id,
                count=item.count,
                variant_id=item.variant_id
            )
            for item in order.dishes
        ]
        
        session.add_all(order_items)
        await session.commit()

        return {"status": "success", "order_id": new_order.id}