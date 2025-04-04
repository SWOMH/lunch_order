from fastapi import HTTPException
from sqlalchemy import select, tuple_
from custom_types import OrderType
from database.decorators import connection
from database.main_connect import DataBaseMainConnect
from database.models.lunch import Dish, User, Order, OrderItem, DishVariant
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

        # Собираем все dish_id и variant_id (где они есть)
        dish_ids = [item.dish_id for item in order.dishes]
    
    # Получаем все блюда
        dishes = await session.scalars(select(Dish).where(Dish.id.in_(dish_ids)))
        dishes = dishes.all()
        dish_map = {dish.id: dish for dish in dishes}

        # Проверяем существование всех блюд
        not_found_dishes = [id_ for id_ in dish_ids if id_ not in dish_map]
        if not_found_dishes:
            raise HTTPException(
                status_code=400,
                detail=f"Блюда не найдены: {not_found_dishes}"
            )

        # Получаем все variant_id из заказа (где они есть)
        variant_items = [item for item in order.dishes if item.variant_id is not None]
        variant_ids = [item.variant_id for item in variant_items]
        
        # Получаем все варианты
        variants = await session.scalars(
            select(DishVariant).where(DishVariant.id.in_(variant_ids))
        )
        variants = variants.all()
        variant_map = {variant.id: variant for variant in variants}

        # Проверяем существование всех вариантов
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

        # Расчет суммы заказа
        amount = 0.0
        for item in order.dishes:
            if item.variant_id:
                # Для блюд с вариантами берем цену из варианта
                variant = variant_map[item.variant_id]
                amount += variant.price * item.count
            else:
                # Для обычных блюд берем цену из самого блюда
                dish = dish_map[item.dish_id]
                if dish.price is None:
                    raise HTTPException(
                        status_code=400,
                        detail=f"У блюда {dish.id} не указана цена"
                    )
                amount += dish.price * item.count

        # Создание заказа
        new_order = Order(user_id=user.id, amount=amount)
        session.add(new_order)
        await session.flush()

        # Создание элементов заказа
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