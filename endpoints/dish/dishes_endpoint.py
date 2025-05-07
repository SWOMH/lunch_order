from fastapi import APIRouter, HTTPException, Path
from database.bloc import database_dish
from database.dish_list import dishes
from custom_types import DishType

router = APIRouter(
    prefix='/dish'
)


@router.get("", tags=["dish"])
async def get_lunch():
    dishes = await database_dish.get_all_dishes_with_variants()
    return {
        "dishes": [
            {
                "id": dish_id,
                "_id": dish_data["_id"],
                "name": dish_data["dish_name"],
                "description": dish_data["description"],
                "image": dish_data["image"],
                "available": dish_data["available"],
                "type": dish_data['type'],
                "price": dish_data['price'] if dish_data['price'] else None, 
                "stop_list": dish_data["stop_list"],
                "is_combo": dish_data["is_combo"],
                "variants": dish_data["variants"],
                "additives": dish_data["additives"]                
            }
            for dish_id, dish_data in dishes.items()
        ]
    }


@router.get("/all_dish", tags=['dish'])
async def get_all_dish():
    # Хз насколько это хороший вариант бить это на 2 эндпоинта
    # пока оставлю так, потом подумаю объединять все в один эндпоинт или вообще просто отдавать все блюда и на фронте
    # фильтровать уже
    dishes = await database_dish.get_all_dishes_for_admin()
    return {
        "dishes": [
            {
                "id": dish_id,
                "_id": dish_data["_id"],
                "name": dish_data["dish_name"],
                "id_iiko": dish_data["id_iiko"],
                "description": dish_data["description"],
                "image": dish_data["image"],
                "available": dish_data["available"],
                "type": dish_data['type'],
                "price": dish_data['price'] if dish_data['price'] else None, 
                "stop_list": dish_data["stop_list"],
                "is_combo": dish_data["is_combo"],
                "variants": dish_data["variants"],
                "additives": dish_data["additives"]                
            }
            for dish_id, dish_data in dishes.items()
        ]
    }

@router.get("/{dish_id}", tags=["dish"])
async def get_dish(dish_id: int = Path(..., gt=0, description="ID блюда")):
    try:
        dish_data = await database_dish.get_dish_by_id(dish_id)
        return {"status": "ok", "dish": dish_data}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при получении блюда: {str(e)}"
        )


@router.post("/add", tags=["dish"])
async def add_dish(dish: DishType):
    try:
        result = await database_dish.add_dish(dish)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при добавлении блюда: {str(e)}"
        )


@router.put("/update/{dish_id}", tags=["dish"])
async def update_dish(dish: DishType, dish_id: int = Path(..., gt=0, description="ID блюда")):
    try:
        result = await database_dish.update_dish(dish_id, dish)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при обновлении блюда: {str(e)}"
        )
