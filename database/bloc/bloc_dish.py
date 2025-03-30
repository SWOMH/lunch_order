from database.main_connect import DataBaseMainConnect
from database.models.lunch import DishVariant, Dish
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
import uuid

class DataBaseDish(DataBaseMainConnect):

    async def get_all_dishes_with_variants(self):
        async with self.Session as session:
            query = (
                select(Dish, DishVariant)
                .outerjoin(DishVariant, Dish.id == DishVariant.dish_id)
                .all()
            )
            result = {}
            for dish, variant in query:
                if dish.id not in result:
                    result[dish.id] = {
                        "dish_name": dish.dish_name,
                        "description": dish.description,
                        "available": dish.available,
                        "stop_list": dish.stop_list,
                        "variants": []
                    }
                if variant:
                    result[dish.id]["variants"].append({
                        "size": variant.size,
                        "price": variant.price
                    })
    
            return result

    async def add_dishes_to_db(self, dishes: list):
        async with self.Session() as session:
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
                        available=bool(dish_data.get("available", True)),
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