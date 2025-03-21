from sqlalchemy import ForeignKey, Time, Column, Integer, Float, String, Date, Boolean, DateTime
from ..base import Base
from datetime import datetime

# TABLE REVENUE =============================================>


class Dish(Base):
    __tablename__ = 'dish'
    id = Column(Integer, primary_key=True)
    dish_name = Column(String, nullable=False)  # Блюдо
    description = Column(String)  # Описание
    price = Column(Float, nullable=True)  # Цена
    available = Column(Boolean, default=True, nullable=False)  # Достпно для заказа
    image = Column(String)  # Картинка блюда
    type = Column(String, nullable=False)  # Тип блюда
    stop_list = Column(Boolean, default=False)  # на стопе ли блюдо?


class DishVariant(Base):
    __tablename__ = 'dish_variant'
    id = Column(Integer, primary_key=True)
    dish_id = Column(Integer, ForeignKey('public.dish.id', ondelete='CASCADE'), nullable=False)
    size = Column(String, nullable=False)  # Размер/вариант блюда (например, "Маленький", "Большой")
    price = Column(Float, nullable=False)  # Цена для этого варианта


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer)
    telegram_name = Column(String)
    telegram_username = Column(String)
    full_name = Column(String, nullable=False)
    is_support = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)


class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)  # Уникальный номер заказа
    user_id = Column(Integer, ForeignKey('public.user.id'), nullable=False)  # Кто сделал заказ
    datetime = Column(DateTime, default=datetime.now())  # Когда сделан заказ


class OrderItem(Base):
    __tablename__ = 'order_items'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('public.orders.id'))  # Ссылка на заказ
    dish_id = Column(Integer, ForeignKey('public.dish.id'))  # Ссылка на блюдо
    quantity = Column(Integer, default=1)  # Количество блюд
