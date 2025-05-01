from fastapi import APIRouter, HTTPException
from custom_types import EditStatusOrderType, OrderType, RemoveDishFromOrder, TelegramId
from database.bloc import database_order, database_user

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
    
    
@router.post("/edit_status", tags=['order'])
async def edit_status_order(order: EditStatusOrderType):
    try:
        if await database_user.get_user_permission(order.telegram_id):
            await database_order.edit_order_status(order.order_id, order.new_status)
            return {"status": "ok", "message":"Статус изменен"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при изменении статуса заказа: {str(e)}"
        )
    
@router.post("/remove_dish_from_order", tags=['order'])
async def remove_dish_from_order(request: RemoveDishFromOrder):
    try:
        result = await database_order.remove_dish_from_order(request)
        return {"status": "ok", "data": result}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при удалении блюда из заказа: {str(e)}"
        )