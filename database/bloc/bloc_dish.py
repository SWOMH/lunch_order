from custom_types import DishType
from database.decorators import connection
from database.main_connect import DataBaseMainConnect
from database.models.lunch import DishVariant, Dish
from sqlalchemy.future import select
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException

class DataBaseDish(DataBaseMainConnect):

    @connection
    async def get_all_dishes_with_variants(self, session: AsyncSession):
        query = (
            select(Dish, DishVariant)
            .outerjoin(DishVariant, Dish.id == DishVariant.dish_id)
            .where(Dish.available == True)
        )
        query_result = await session.execute(query)
        result = {}
        for dish, variant in query_result:
            # if dish.available:
            if dish.id not in result:
                result[dish.id] = {
                    "_id": dish._id,
                    "dish_name": dish.dish_name,
                    "description": dish.description,
                    "image": dish.image if dish.image else None,
                    "available": dish.available,
                    "type": dish.type,
                    "price": dish.price if dish.price else None,
                    "stop_list": dish.stop_list,
                    "additives": dish.additives,
                    "is_combo": dish.is_combo,
                    "variants": []
                }
            if variant:
                result[dish.id]["variants"].append({
                    "id": variant.id,
                    "size": variant.size,
                    "price": variant.price
                })

        return result
    
    @connection
    async def get_all_dishes_for_admin(self, session: AsyncSession):
        query = (
            select(Dish, DishVariant)
            .outerjoin(DishVariant, Dish.id == DishVariant.dish_id)
        )
        query_result = await session.execute(query)
        result = {}
        for dish, variant in query_result:
            if dish.id not in result:
                result[dish.id] = {
                    "_id": dish._id,
                    "id_iiko": dish.id_iiko,
                    "dish_name": dish.dish_name,
                    "description": dish.description,
                    "image": dish.image if dish.image else None,
                    "available": dish.available,
                    "type": dish.type,
                    "price": dish.price if dish.price else None,
                    "stop_list": dish.stop_list,
                    "additives": dish.additives,
                    "is_combo": dish.is_combo,
                    "variants": []
                }
            if variant:
                result[dish.id]["variants"].append({
                    "id": variant.id,
                    "size": variant.size,
                    "price": variant.price
                })

        return result

    @connection
    async def add_dishes_to_db(self, dishes: list, session: AsyncSession):
        for dish_data in dishes:
            query = select(Dish).filter_by(dish_name=dish_data["dish_name"])
            result = await session.execute(query)
            dish = result.scalar_one_or_none()
            
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
                await session.flush()

            
            for variant_data in variants:
                size = variant_data.get("size")
                price = variant_data.get("price")

                if size and price:
                    query = select(DishVariant).filter_by(dish_id=dish.id, size=size)
                    result = await session.execute(query)
                    variant = result.scalar_one_or_none()
                    
                    if not variant:
                        variant = DishVariant(dish_id=dish.id, size=size, price=price)
                        session.add(variant)    
        await session.commit()

    @connection
    async def add_dish(self, dish_data: DishType, session: AsyncSession):
        query = select(Dish).filter_by(dish_name=dish_data.dish_name)
        result = await session.execute(query)
        existing_dish = result.scalar_one_or_none()
        
        if existing_dish:
            raise HTTPException(
                status_code=400,
                detail=f"Блюдо с названием '{dish_data.dish_name}' уже существует"
            )
        
        new_dish = Dish(
            _id=str(uuid.uuid4()),
            dish_name=dish_data.dish_name,
            description=dish_data.description,
            price=dish_data.price,
            available=dish_data.available,
            image=str(dish_data.image) if dish_data.image else None,
            type=dish_data.type,
            stop_list=dish_data.stop_list,
            is_combo=dish_data.is_combo,
            additives=len(dish_data.variants) > 0
        )
        
        session.add(new_dish)
        await session.flush()
        
        if dish_data.variants is not None:
            for variant_data in dish_data.variants:
                variant = DishVariant(
                    dish_id=new_dish.id,
                    size=variant_data.size,
                    price=variant_data.price
                )
                session.add(variant)
        
        await session.commit()
        
        return {
            "status": "success",
            "dish_id": new_dish.id,
            "message": f"Блюдо '{new_dish.dish_name}' успешно добавлено"
        }
    
    @connection
    async def update_dish(self, dish_id: int, dish_data, session: AsyncSession):
        query = select(Dish).filter_by(id=dish_id)
        result = await session.execute(query)
        dish = result.scalar_one_or_none()
        
        if not dish:
            raise HTTPException(
                status_code=404,
                detail=f"Блюдо с ID {dish_id} не найдено"
            )
        
        if dish_data.dish_name is not None:
            dish.dish_name = dish_data.dish_name
        if dish_data.description is not None:
            dish.description = dish_data.description
        if dish_data.price is not None or dish_data.price == 0:
            dish.price = dish_data.price
        if dish_data.available is not None:
            dish.available = dish_data.available
        if dish_data.image is not None:
            dish.image = str(dish_data.image)
        if dish_data.type is not None:
            dish.type = dish_data.type
        if dish_data.stop_list is not None:
            dish.stop_list = dish_data.stop_list
        if dish_data.is_combo is not None:
            dish.is_combo = dish_data.is_combo
        
        if dish_data.variants is not None:
            query = select(DishVariant).filter_by(dish_id=dish_id)
            result = await session.execute(query)
            current_variants = result.scalars().all()
            
            variants_to_keep = set()
            
            for variant_data in dish_data.variants:
                existing_variant = None
                for var in current_variants:
                    if var.size == variant_data.size:
                        existing_variant = var
                        break
                
                if existing_variant:
                    existing_variant.price = variant_data.price
                    variants_to_keep.add(existing_variant.id)
                else:
                    new_variant = DishVariant(
                        dish_id=dish_id,
                        size=variant_data.size,
                        price=variant_data.price
                    )
                    session.add(new_variant)
            
            for var in current_variants:
                if var.id not in variants_to_keep:
                    await session.delete(var)
            
            dish.additives = len(dish_data.variants) > 0
        
        await session.commit()
        
        return {
            "status": "success",
            "message": f"Блюдо '{dish.dish_name}' успешно обновлено"
        }

    @connection
    async def get_dish_by_id(self, dish_id: int, session: AsyncSession):
        query = select(Dish).filter_by(id=dish_id)
        result = await session.execute(query)
        dish = result.scalar_one_or_none()
        
        if not dish:
            raise HTTPException(
                status_code=404,
                detail=f"Блюдо с ID {dish_id} не найдено"
            )
        
        query = select(DishVariant).filter_by(dish_id=dish_id)
        result = await session.execute(query)
        variants = result.scalars().all()
        
        dish_data = {
            "id": dish.id,
            "_id": dish._id,
            "dish_name": dish.dish_name,
            "description": dish.description,
            "price": dish.price,
            "available": dish.available,
            "image": dish.image,
            "type": dish.type,
            "stop_list": dish.stop_list,
            "is_combo": dish.is_combo,
            "additives": dish.additives,
            "variants": [
                {
                    "id": variant.id,
                    "size": variant.size,
                    "price": variant.price
                }
                for variant in variants
            ]
        }
        
        return dish_data
    
    