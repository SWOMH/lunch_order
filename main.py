from fastapi import FastAPI, Request
from endpoints.dish.dishes_endpoint import router as dish_router
from endpoints.user.user_endpoint import router as user_router
from endpoints.order.orders_endpoint import router as order_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(root_path="/api")

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Forwarded-Proto"] = "https"
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dish_router)
app.include_router(user_router)
app.include_router(order_router)