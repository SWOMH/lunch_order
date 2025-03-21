from fastapi import HTTPException
from database.main_connect import DataBaseMainConnect
from database.models.lunch import User, Dish, Order, OrderItem, DishVariant


class DatabaseUser(DataBaseMainConnect):

    def get_user(self, id: int) -> str:
        session = self.Session()
        with session:
            user = session.query(User).filter_by(telegram_id=id).first()
            if not user:
                raise HTTPException(status_code=404, detail="Пользователь не найден")
            return user.full_name

    def register_user(self, id: int, full_name: str):
        session = self.Session()
        with session:
            existing_user = session.query(User).filter_by(telegram_id=id).first()
            if existing_user:
                raise HTTPException(status_code=400, detail="Пользователь с таким Telegram ID уже существует")

            new_user = User(telegram_id=id, full_name=full_name)
            session.add(new_user)
            session.commit()
            return {"message": "Пользователь успешно зарегистрирован", "telegram_id": id,
                    "full_name": full_name}








