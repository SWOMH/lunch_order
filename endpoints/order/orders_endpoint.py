from fastapi import APIRouter, HTTPException
from custom_types import OrderType
from database.bloc import database_order

router = APIRouter(
    prefix='/order'
    )


@router.post("", tags=["order"])
async def ordering_food(order: OrderType):
    try:
        result = await database_order.ordering_food(order)
        return {"status": "ok", "data": result}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при создании заказа: {str(e)}"
        )
    
    # {
#   "detail": "Ошибка при создании заказа: (sqlalchemy.dialects.postgresql.asyncpg.Error) 
#   <class 'asyncpg.exceptions.InvalidTextRepresentationError'>: 
#   неверное значение для перечисления order_status_enum: 
#   \"formalized\"\n[SQL: INSERT INTO public.orders (user_id, amount, order_status)
#     VALUES ($1::INTEGER, $2::FLOAT, $3::order_status_enum) RETURNING public.orders.id, public.orders.datetime]
#     \n[parameters: (1, 770.0, 'formalized')]\n(Background on this error at: https://sqlalche.me/e/20/dbapi)"
# }