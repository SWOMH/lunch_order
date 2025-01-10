from fastapi import HTTPException

from core import DatabaseCore
import os
from models.lunch import User, Dish, Order, OrderItem

class Database(DatabaseCore):
    def __init__(self):
        user = os.getenv('POSTGRES_USER')
        password = os.getenv('POSTGRES_PASSWORD')
        host = os.getenv('POSTGRES_HOST')
        port = os.getenv('POSTGRES_PORT')
        database = os.getenv('POSTGRES_DB_NAME')

        if not all([user, password, host, port, database]):
            raise ValueError("One or more environment variables are not set.")

        url_con = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
        super().__init__(str(url_con), create_tables=True)

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

