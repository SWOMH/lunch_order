from sqlalchemy import ForeignKey, Time, Column, Integer, Float, String, Date, Boolean, DateTime
from ..core import Base
from datetime import datetime

# TABLE REVENUE =============================================>


class Dish(Base):
    __tablename__ = 'dish'
    id = Column(Integer, primary_key=True)
    dish_name = Column(String)  # Блюдо
    description = Column(String)
    price = Column(Float)  # Цена
    available = Column(Boolean)  # Достпно для заказа
    image = Column(String)  # Картинка блюда


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer)
    full_name = Column(String)


class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)  # Уникальный номер заказа
    user_id = Column(Integer, ForeignKey('public.user.id'))  # Кто сделал заказ
    datetime = Column(DateTime, default=datetime.now())  # Когда сделан заказ


class OrderItem(Base):
    __tablename__ = 'order_items'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('public.orders.id'))  # Ссылка на заказ
    dish_id = Column(Integer, ForeignKey('public.dish.id'))  # Ссылка на блюдо
    quantity = Column(Integer, default=1)  # Количество блюд
