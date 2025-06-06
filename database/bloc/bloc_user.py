from fastapi import HTTPException
from custom_types import TelegramId, UserSchema
from datetime import datetime
from database.main_connect import DataBaseMainConnect
from database.models.lunch import User, Dish, Order, OrderItem, DishVariant
from database.decorators import connection
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload


class DatabaseUser(DataBaseMainConnect):

    @connection
    async def get_user_permission(self, id: int, session: AsyncSession) -> dict:
        user = await session.scalar(select(User).filter_by(telegram_id=id))
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        if user.is_admin and not user.banned:
            return True
        else:
            return False # Потом исправлю, если неправильно написал, да и вообще нужно все стандартизировать

    @connection
    async def get_all_users(self, session: AsyncSession) -> dict:
        result = await session.execute(select(User))
        return {"users": [{"id": u.id, "telegram_id": u.telegram_id, "name": u.full_name, "telegram_name": u.telegram_name, "telegram_username": u.telegram_username, "banned": u.banned} for u in result.scalars()]}

    @connection
    async def get_user(self, id: int, session: AsyncSession) -> dict:
        user = await session.scalar(select(User).filter_by(telegram_id=id))
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")        
        return {"user": {
            "id": user.id,
            "telegram_id": user.telegram_id,
            "telegram_user_name": user.telegram_username,
            "telegram_name": user.telegram_name,
            "full_name": user.full_name,
            "ban": user.banned,
            "admin": user.is_admin
        }}
    

    @connection
    async def register_user(self, user_info: UserSchema, session: AsyncSession) -> dict:
        query = select(User).filter_by(telegram_id=user_info.telegram_id)
        user = await session.execute(query)
        existing_user = user.scalar_one_or_none()
        if existing_user:
            raise HTTPException(status_code=400, detail="Пользователь с таким Telegram ID уже существует")

        new_user = User(telegram_id=user_info.telegram_id, full_name=user_info.full_name, 
                        telegram_name=user_info.telegram_name, telegram_username=user_info.telegram_username)
        session.add(new_user)
        await session.commit()
        return {"message": "Пользователь успешно зарегистрирован", "telegram_id": user_info.telegram_id,
                "full_name": user_info.full_name}
    
    @connection
    async def get_user_orders_and_actual(self, telegram_id: int, session: AsyncSession, actual_orders: bool = None) -> dict:
        user = await session.scalar(
            select(User).where(User.telegram_id == telegram_id))
        
        if not user:
            raise HTTPException(
                status_code=403,
                detail="User not found"
            )
        if actual_orders:
            today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            orders = await session.execute(
                select(Order)
                .where(Order.datetime >= today_start, Order.user_id == user.id)
                .options(
                    selectinload(Order.user),
                    selectinload(Order.order_items).selectinload(OrderItem.dish),
                    selectinload(Order.order_items).selectinload(OrderItem.variant)
                )
                .order_by(Order.datetime.desc())
            )
        else:
            orders = await session.execute(
                select(Order)
                .where(Order.user_id == user.id)
                .options(
                    selectinload(Order.user),
                    selectinload(Order.order_items).selectinload(OrderItem.dish),
                    selectinload(Order.order_items).selectinload(OrderItem.variant)
                )
                .order_by(Order.datetime.desc())
            )
        orders = orders.scalars().all()
        
        result = []
        for order in orders:
            order_data = {
                "order_id": order.id,
                "user": {
                    "telegram_id": order.user.telegram_id,
                    "full_name": order.user.full_name
                },
                "datetime": order.datetime.isoformat(),
                "amount": order.amount,
                "status": order.order_status.value,
                "items": []
            }
            
            for item in order.order_items:
                item_data = {
                    "dish_id": item.dish_id,
                    "dish_name": item.dish.dish_name if item.dish else "Unknown dish",
                    "count": item.count,
                    "price": item.variant.price if item.variant else (item.dish.price if item.dish else 0)
                }
                if item.variant:
                    item_data["variant"] = {
                        "id": item.variant.id,
                        "size": item.variant.size
                    }
                order_data["items"].append(item_data)
            
            result.append(order_data)

        if len(result) == 0 and actual_orders:
            return {"orders": "You didn't order anything today"}
        if len(result) == 0:
            return {"orders": "You didn't order anything"}
        return {"orders": result}


    @connection
    async def edit_user_status(self, telegram_id_user: int, session: AsyncSession) -> dict:
        user = await session.scalar(
            select(User).where(User.telegram_id == telegram_id_user))
        
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
            
        if user.banned:
            user.banned = False
        else:
            user.banned = True
        
        await session.commit()
        return {"status": "ok",
                "message": f"У {user.full_name} изменен статус на {user.banned}"}

        





