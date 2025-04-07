from fastapi import FastAPI
from endpoints.dish.dishes_endpoint import router as dish_router
from endpoints.user.user_endpoint import router as user_router
from endpoints.order.orders_endpoint import router as order_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.include_router(dish_router)
app.include_router(user_router)
app.include_router(order_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Разрешенный origin
    allow_credentials=True,
    allow_methods=["*"],  # Разрешить все методы (GET, POST, PUT и т. д.)
    allow_headers=["*"],  # Разрешить все заголовки
)