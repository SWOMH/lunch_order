from fastapi import APIRouter, HTTPException
from custom_types import OrderType, TelegramId
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
    
@router.post("/actual_orders", tags=["order"])
async def get_actual_orders(telegram_id: TelegramId):
    try:
        result = await database_order.get_actual_orders(telegram_id)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка: {str(e)}"
        )
    