from fastapi import HTTPException
from .core import DatabaseCore
import os
from .models.lunch import User, Dish, Order, OrderItem, DishVariant
from dotenv import load_dotenv

load_dotenv()


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

    def get_all_dishes_with_variants(self):
        session = self.Session()
        with session:
            query = (
                session.query(Dish, DishVariant)
                .outerjoin(DishVariant, Dish.id == DishVariant.dish_id)
                .all()
            )
            result = {}
            for dish, variant in query:
                if dish.id not in result:
                    result[dish.id] = {
                        "dish_name": dish.dish_name,
                        "description": dish.description,
                        "available": dish.available,
                        "stop_list": dish.stop_list,
                        "variants": []
                    }
                if variant:
                    result[dish.id]["variants"].append({
                        "size": variant.size,
                        "price": variant.price
                    })

            return result

    def ordering_food(self, foods: list[int], telegram_id: int):
        session = self.Session()
        with session.no_autoflush:
            dishes = session.query(Dish).filter(Dish.id.in_(foods)).all()
            if not dishes or len(dishes) != len(foods):
                raise HTTPException(status_code=400, detail="Некоторые блюда не найдены")
            user = session.query(User).filter_by(telegram_id=telegram_id).first()
            new_order = Order(
                user_id=user.id
            )
            session.add(new_order)
            session.flush()
            order_items = []
            for dish_id in foods:
                order_items.append(OrderItem(order_id=new_order.id, dish_id=dish_id))
            session.bulk_save_objects(order_items)
            session.commit()
            return HTTPException(status_code=200, detail="Заказ добавлен")



    # def add_dishes_to_db(self, dishes: list):
    #     session = self.Session()
    #     with session:
    #         for dish_data in dishes:
    #             # Создаем или находим запись для блюда
    #             dish = session.query(Dish).filter_by(dish_name=dish_data["dish_name"]).first()
    #             if not dish:
    #                 dish = Dish(
    #                     dish_name=dish_data["dish_name"],
    #                     description=dish_data.get("description", ""),
    #                     available=bool(dish_data.get("available", True)),
    #                     price=dish_data.get("price") if dish_data.get("price") != '' else None,
    #                     image=dish_data.get("image", ""),
    #                     type=dish_data.get("type", ""),
    #                     stop_list=False
    #                 )
    #                 session.add(dish)
    #                 session.flush()  # Сохраняем, чтобы получить ID блюда
    #
    #             # Если есть варианты, добавляем их
    #             variants = dish_data.get("variants", [])
    #             for variant_data in variants:
    #                 size = variant_data.get("size")
    #                 price = variant_data.get("price")
    #
    #                 if size and price:
    #                     # Проверяем, есть ли уже такой вариант для блюда
    #                     variant = session.query(DishVariant).filter_by(dish_id=dish.id, size=size).first()
    #                     if not variant:
    #                         variant = DishVariant(dish_id=dish.id, size=size, price=price)
    #                         session.add(variant)
    #
    #             # Если у блюда нет вариантов, добавляем его цену в качестве единственного варианта
    #             # if not variants and dish_data.get("price"):
    #             #     price_variant = DishVariant(
    #             #         dish_id=dish.id,
    #             #         size="Стандарт",
    #             #         price=dish_data["price"]
    #             #     )
    #             #     session.add(price_variant)
    #
    #         session.commit()  # Сохраняем изменения
