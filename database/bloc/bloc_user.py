from fastapi import HTTPException
from database.main_connect import DataBaseMainConnect
from database.models.lunch import User, Dish, Order, OrderItem, DishVariant
from database.decorators import connection
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

class DatabaseUser(DataBaseMainConnect):

    @connection
    async def get_user(self, id: int, session: AsyncSession) -> str:
        user = await session.scalar(select(User).filter_by(telegram_id=id))
        if not user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        return {"user": {
            "id": user.id,
            "user_name": user.full_name
        }}
    

    @connection
    async def register_user(self, id: int, full_name: str, session: AsyncSession):        
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








