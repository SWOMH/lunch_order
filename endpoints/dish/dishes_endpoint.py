from fastapi import APIRouter
from database.bloc import database_dish
from database.dish_list import dishes

router = APIRouter(
    prefix='/dish'
)


@router.get("", tags=["dish"])
async def get_lunch():
    dishes = await database_dish.get_all_dishes_with_variants()
    return {
        "status": "ok",
        "dishes": [
            {
                "id": dish_id,
                "_id": dish_data["_id"],
                "name": dish_data["dish_name"],
                "description": dish_data["description"],
                "image": dish_data["image"],
                "available": dish_data["available"],
                "stop_list": dish_data["stop_list"],
                "variants": dish_data["variants"],
                "additives": dish_data["additives"]                
            }
            for dish_id, dish_data in dishes.items()
        ]
    }


@router.get("/adding_dish", tags=["dish"])
async def add_dishes_list():
    await database_dish.add_dishes_to_db(dishes)
    return {"message": "Все загружено в БД"}
