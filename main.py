from typing import Union
from fastapi import FastAPI
from custom_types import UserSchema
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
def get_lunch():
    dishes = database_dish.get_all_dishes_with_variants()
    return {
        "dishes": [
            {
                "id": dish_id,
                "name": dish_data["dish_name"],
                "description": dish_data["description"],
                "available": dish_data["available"],
                "stop_list": dish_data["stop_list"],
                "variants": dish_data["variants"]
            }
            for dish_id, dish_data in dishes.items()
        ]
    }


    # dishes = db.get_all_dishes_with_variants()
    # print(dishes)
    # return {"dishes": [{"id": dish.id, "name": dish.name, "description": dish.description} for dish in dishes]}

@app.post("/ordering_food")
def ordering_food(foods: list[int], telegram_id: int):
    return {"order_details": ordering_food(foods, telegram_id)}

# @app.get("/adding_dish")
# def add_dishes_list():
#     db.add_dishes_to_db(dishes)
#     return {"message": "Все загружено в БД"}
