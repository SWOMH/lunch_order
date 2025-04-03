from fastapi import APIRouter, HTTPException
from custom_types import OrderType
from database.bloc import database_order

router = APIRouter(
    prefix='/order'
    )


@router.post("/ordering_food")
def ordering_food(order: OrderType):
    try:
        result = database_order.ordering_food(order)
        return {"status": "ok", "data": result}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при создании заказа: {str(e)}"
        )