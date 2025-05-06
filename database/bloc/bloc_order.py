from datetime import datetime, timezone
from typing import Literal
from fastapi import HTTPException
from sqlalchemy import delete, func, select, tuple_
from custom_types import EditOrder, OrderType, RemoveDishFromOrder, TelegramId
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
    async def get_today_orders_formatted(session: AsyncSession) -> list[dict]:
        """Получает заказы за сегодня и возвращает для Telegram"""
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


    @connection
    async def edit_order_status(self, order_id: int, status: Literal["formalized", "completed", 
                        "canceled", "deleted", "unknown"], session: AsyncSession):        
        order = await session.execute(
            select(Order)
            .where(Order.id >= order_id))
        order = order.scalars().first()
        order.order_status = status
        session.commit()

    @connection
    async def edit_order(self, order: EditOrder, session: AsyncSession):
        user = await session.scalar(
            select(User).where(User.telegram_id == order.telegram_id))
        
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        if user.banned:
            raise HTTPException(
                status_code=403,
                detail="Операция недоступна: пользователь заблокирован"
            )

        existing_order = await session.scalar(
            select(Order).where(Order.id == order.order_id))
        
        if not existing_order:
            raise HTTPException(status_code=404, detail="Заказ не найден")
        
        if existing_order.user_id != user.id and not user.admin:
            raise HTTPException(
                status_code=403,
                detail="Недостаточно прав для редактирования этого заказа"
            )

        if existing_order.status not in ["formalized", "unknown"]:
            raise HTTPException(
                status_code=400,
                detail="Нельзя редактировать заказ в текущем статусе"
            )

        await session.execute(
            delete(OrderItem).where(OrderItem.order_id == existing_order.id)
        )

        dish_ids = [item.dish_id for item in order.order]
        dishes = await session.scalars(select(Dish).where(Dish.id.in_(dish_ids)))
        dishes = dishes.all()
        dish_map = {dish.id: dish for dish in dishes}

        not_found_dishes = [id_ for id_ in dish_ids if id_ not in dish_map]
        if not_found_dishes:
            raise HTTPException(
                status_code=400,
                detail=f"Блюда не найдены: {not_found_dishes}"
            )

        variant_items = [item for item in order.order if item.variant_id is not None]
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
        order_items = []
        for item in order.order:
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

            order_items.append(OrderItem(
                order_id=existing_order.id,
                dish_id=item.dish_id,
                count=item.count,
                variant_id=item.variant_id
            ))
        
        existing_order.amount = amount
        session.add_all(order_items)
        await session.commit()

        return {"order_id": existing_order.id}


    @connection
    async def remove_dish_from_order(self, request: RemoveDishFromOrder, session: AsyncSession):        
        user = await session.scalar(
            select(User).where(User.telegram_id == request.telegram_id))
        
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        
        if user.banned:
            raise HTTPException(
                status_code=403,
                detail="Операция недоступна: пользователь заблокирован"
            )

        order = await session.scalar(
            select(Order).where(Order.id == request.order_id))
        
        if not order:
            raise HTTPException(status_code=404, detail="Заказ не найден")
        
        if order.user_id != user.id and not user.admin:
            raise HTTPException(
                status_code=403,
                detail="Недостаточно прав для редактирования этого заказа"
            )

        if order.order_status not in ["formalized", "unknown"]:
            raise HTTPException(
                status_code=400,
                detail="Нельзя редактировать заказ в текущем статусе"
            )

        query = select(OrderItem).where(
            OrderItem.order_id == request.order_id,
            OrderItem.dish_id == request.dish_id
        )
        
        if request.variant_id:
            query = query.where(OrderItem.variant_id == request.variant_id)
        
        items_to_remove = await session.scalars(query)
        items_to_remove = items_to_remove.all()
        
        if not items_to_remove:
            raise HTTPException(
                status_code=404,
                detail="Указанное блюдо не найдено в заказе"
            )

        total_removed = 0.0
        for item in items_to_remove:
            if item.variant_id:
                variant = await session.scalar(
                    select(DishVariant).where(DishVariant.id == item.variant_id))
                total_removed += variant.price * item.count
            else:
                dish = await session.scalar(
                    select(Dish).where(Dish.id == item.dish_id))
                if dish.price:
                    total_removed += dish.price * item.count
            
            await session.delete(item)

        order.amount = max(0, order.amount - total_removed)
        
        remaining_items = await session.scalar(
            select(func.count(OrderItem.id)).where(OrderItem.order_id == order.id))
        
        if remaining_items == 0:
            order.order_status = "deleted"

        await session.commit()

        return {"order_id": order.id, "new_amount": order.amount}