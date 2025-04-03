from fastapi import FastAPI, HTTPException
from custom_types import OrderType, TelegramId, UserSchema
from database.bloc import *
from database.dish_list import dishes
from endpoints.dish.dishes_endpoint import router as dish_router
from endpoints.user.user_endpoint import router as user_router

app = FastAPI()
app.include_router(dish_router)
app.include_router(user_router)




@app.post("/ordering_food")
def ordering_food(order: OrderType):
    db_order = DatabaseOrder()
    try:
        result = db_order.ordering_food(order)
        return {"status": "ok", "data": result}
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
