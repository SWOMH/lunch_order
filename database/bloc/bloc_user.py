from fastapi import HTTPException
from database.main_connect import DataBaseMainConnect
from database.models.lunch import User, Dish, Order, OrderItem, DishVariant
from database.decorators import connection
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

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
        return {"status": "ok",
                "users": [{"id": u.id, "name": u.full_name, "banned": u.banned} for u in result.scalars()]}

    @connection
    async def get_user(self, id: int, session: AsyncSession) -> dict:
        user = await session.scalar(select(User).filter_by(telegram_id=id))
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")        
        return {"user": {
            "id": user.id,
            "telegram_user_name": user.telegram_username,
            "telegram_name": user.telegram_name,
            "full_name": user.full_name,
            "ban": user.banned,
            "admin": user.is_admin
        }}
    

    @connection
    async def register_user(self, id: int, full_name: str, session: AsyncSession) -> dict:
        query = select(User).filter_by(telegram_id=id)
        user = await session.execute(query)
        existing_user = user.scalar_one_or_none()
        if existing_user:
            raise HTTPException(status_code=400, detail="Пользователь с таким Telegram ID уже существует")

        new_user = User(telegram_id=id, full_name=full_name)
        session.add(new_user)
        await session.commit()
        return {"message": "Пользователь успешно зарегистрирован", "telegram_id": id,
                "full_name": full_name}








