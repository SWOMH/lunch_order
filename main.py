from typing import Union
from fastapi import FastAPI
from database.bloc import Database

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
    dishes = db.get_all_lanch()
    return {"dishes": [{"id": dish.id, "name": dish.name, "description": dish.description} for dish in dishes]}

@app.post("/ordering_food")
def ordering_food(foods: list[int], telegram_id: int):
    return {"order_details": ordering_food(foods, telegram_id)}
