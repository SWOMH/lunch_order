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

