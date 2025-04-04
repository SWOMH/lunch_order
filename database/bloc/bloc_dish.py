from database.decorators import connection
from database.main_connect import DataBaseMainConnect
from database.models.lunch import DishVariant, Dish
from sqlalchemy.future import select
import uuid
from sqlalchemy.ext.asyncio import AsyncSession

class DataBaseDish(DataBaseMainConnect):

    @connection
    async def get_all_dishes_with_variants(self, session: AsyncSession):
        query = (
            select(Dish, DishVariant)
            .outerjoin(DishVariant, Dish.id == DishVariant.dish_id)
        )
        query_result = await session.execute(query)
        result = {}
        for dish, variant in query_result:
            # if dish.available:
            if dish.id not in result and dish.available:
                result[dish.id] = {
                    "_id": dish._id,
                    "dish_name": dish.dish_name,
                    "description": dish.description,
                    "image": dish.image if dish.image else None,
                    "available": dish.available,
                    "stop_list": dish.stop_list,
                    "additives": dish.additives,
                    "variants": []
                }
            if variant:
                result[dish.id]["variants"].append({
                    "size": variant.size,
                    "price": variant.price
                })

        return result

    @connection
    async def add_dishes_to_db(self, dishes: list, session: AsyncSession):        
        for dish_data in dishes:
            # Создаем или находим запись для блюда
            query = select(Dish).filter_by(dish_name=dish_data["dish_name"])
            result = await session.execute(query)
            dish = result.scalar_one_or_none()
            
            # Если есть варианты, добавляем их на 59 строке
            variants = dish_data.get("variants", [])
            if not dish:
                dish = Dish(
                    _id = str(uuid.uuid4()),
                    dish_name=dish_data["dish_name"],
                    description=dish_data.get("description", ""),
                    # available=bool(dish_data.get("available", True)),
                    available=True,
                    price=dish_data.get("price") if dish_data.get("price") != '' else None,
                    image=dish_data.get("image", ""),
                    type=dish_data.get("type", ""),
                    stop_list=False,
                    is_combo = False,
                    additives= True if variants else False,
                )
                session.add(dish)
                await session.flush()  # Сохраняем, чтобы получить ID блюда

            
            for variant_data in variants:
                size = variant_data.get("size")
                price = variant_data.get("price")

                if size and price:
                    # Проверяем, есть ли уже такой вариант для блюда
                    query = select(DishVariant).filter_by(dish_id=dish.id, size=size)
                    result = await session.execute(query)
                    variant = result.scalar_one_or_none()
                    
                    if not variant:
                        variant = DishVariant(dish_id=dish.id, size=size, price=price)
                        session.add(variant)    
        await session.commit()  # Сохраняем изменения