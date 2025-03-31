from fastapi import FastAPI, HTTPException
from custom_types import OrderType, UserSchema
from database.bloc import *
from database.dish_list import dishes


app = FastAPI()


@app.get("/user/{telegram_id}")
def get_user_by_telegram_id(telegram_id: int):
    return {"full_name": database_user.get_user(telegram_id)}


@app.post("/user/register/{telegram_id}")
def register_user(user: UserSchema):
    return {"registration": database_user.register_user(user.telegram_id, user.full_name)}


@app.get("/lunch")
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
                "stop_list": dish_data["stop_list"],
                "variants": dish_data["variants"],
                "additives": dish_data["additives"]                
            }
            for dish_id, dish_data in dishes.items()
        ]
    }


@app.post("/ordering_food")
def ordering_food(order: OrderType):
    db_order = DatabaseOrder()
    try:
        result = db_order.ordering_food(order)
        return {"status": "success", "data": result}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при создании заказа: {str(e)}"
        )

@app.get("/adding_dish")
async def add_dishes_list():
    await database_dish.add_dishes_to_db(dishes)
    return {"message": "Все загружено в БД"}
