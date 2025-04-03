from fastapi import FastAPI
from endpoints.dish.dishes_endpoint import router as dish_router
from endpoints.user.user_endpoint import router as user_router
from endpoints.order.orders_endpoint import router as order_router

app = FastAPI()
app.include_router(dish_router)
app.include_router(user_router)
app.include_router(order_router)
