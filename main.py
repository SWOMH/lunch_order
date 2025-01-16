from typing import Union
from fastapi import FastAPI
from database.bloc import Database
from database.dish_list import dishes

app = FastAPI()
db = Database()

@app.get("/user/{telegram_id}")
def get_user_by_telegram_id(telegram_id: int):
    return {"full_name": db.get_user(telegram_id)}

@app.post("/user/register/{telegram_id}")
def register_user(telegram_id: int, full_name: str):
    return {"registration": db.register_user(telegram_id, full_name)}


@app.get("/lunch")
def get_lunch():
    dishes = db.get_all_dishes_with_variants()
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
