from datetime import datetime, timezone
from typing import Literal
from fastapi import HTTPException
from sqlalchemy import select, tuple_
from custom_types import OrderType, TelegramId
from database.decorators import connection
from database.main_connect import DataBaseMainConnect
from database.models.lunch import Dish, User, Order, OrderItem, DishVariant
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


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

        dish_ids = [item.dish_id for item in order.dishes]
    
        dishes = await session.scalars(select(Dish).where(Dish.id.in_(dish_ids)))
        dishes = dishes.all()
        dish_map = {dish.id: dish for dish in dishes}

        not_found_dishes = [id_ for id_ in dish_ids if id_ not in dish_map]
        if not_found_dishes:
            raise HTTPException(
                status_code=400,
                detail=f"Блюда не найдены: {not_found_dishes}"
            )

        variant_items = [item for item in order.dishes if item.variant_id is not None]
        variant_ids = [item.variant_id for item in variant_items]
        
        variants = await session.scalars(
            select(DishVariant).where(DishVariant.id.in_(variant_ids))
        )
        variants = variants.all()
        variant_map = {variant.id: variant for variant in variants}

        not_found_variants = [
            f"{item.dish_id}/{item.variant_id}" 
            for item in variant_items 
            if item.variant_id not in variant_map
        ]
        if not_found_variants:
            raise HTTPException(
                status_code=400,
                detail=f"Варианты блюд не найдены: {not_found_variants}"
            )

        amount = 0.0
        for item in order.dishes:
            if item.variant_id:
                variant = variant_map[item.variant_id]
                amount += variant.price * item.count
            else:
                dish = dish_map[item.dish_id]
                if dish.price is None:
                    raise HTTPException(
                        status_code=400,
                        detail=f"У блюда {dish.id} не указана цена"
                    )
                amount += dish.price * item.count

        new_order = Order(user_id=user.id, amount=amount)
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

        return {"order_id": new_order.id}
    
    @connection
    async def get_actual_orders(self, telegram_id: TelegramId, session: AsyncSession):
        user = await session.scalar(
            select(User).where(User.telegram_id == telegram_id.telegram_id))
        
        if not user or not user.is_admin:
            raise HTTPException(
                status_code=403,
                detail="Authorization credentials denied"
            )
        
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        orders = await session.execute(
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
        
        result = []
        for order in orders:
            order_data = {
                "order_id": order.id,
                "user": {
                    "telegram_id": order.user.telegram_id,
                    "full_name": order.user.full_name
                },
                "datetime": order.datetime.isoformat(),
                "amount": order.amount,
                "status": order.order_status.value,
                "items": []
            }
            
            for item in order.order_items:
                item_data = {
                    "dish_id": item.dish_id,
                    "dish_name": item.dish.dish_name if item.dish else "Unknown dish",
                    "count": item.count,
                    "price": item.variant.price if item.variant else (item.dish.price if item.dish else 0)
                }
                if item.variant:
                    item_data["variant"] = {
                        "id": item.variant.id,
                        "size": item.variant.size
                    }
                order_data["items"].append(item_data)
            
            result.append(order_data)
        if len(result) == 0:            
            return {"status": "success", "orders": "There are no orders for today"}
        return {"status": "success", "orders": result}


    @connection
    async def edit_order_status(self, order_id: int, status: Literal["formalized", "completed", 
                        "canceled", "deleted", "unknown"], session: AsyncSession):        
        order = await session.execute(
            select(Order)
            .where(Order.id >= order_id))
        order = order.scalars().first()
        order.order_status = status
        session.commit()