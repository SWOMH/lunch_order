from sqlalchemy import ForeignKey, Column, Integer, Float, String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from ..base import Base

# TABLE REVENUE =============================================>


class Dish(Base):
    __tablename__ = 'dish'
    id: Mapped[int] = mapped_column(primary_key=True)
    _id: Mapped[str] = mapped_column(nullable=True)  # Сервисный id блюда
    dish_name: Mapped[str] = mapped_column(nullable=False)  # Блюдо
    description: Mapped[str]  # Описание
    price: Mapped[float] = mapped_column(nullable=True)  # Цена
    available: Mapped[bool] = mapped_column(default=True, nullable=False)  # Доступно для заказа
    image: Mapped[str]  # Картинка блюда
    type: Mapped[str] = mapped_column(nullable=False)  # Тип блюда
    stop_list: Mapped[bool] = mapped_column(default=False)  # На стопе ли блюдо?
    is_combo: Mapped[bool] = mapped_column(default=False, nullable=False)  # Это комбо?
    additives: Mapped[bool] = mapped_column(default=False, nullable=False)  # Есть ли добавки к блюду


class DishVariant(Base):
    __tablename__ = 'dish_variant'
    id: Mapped[int] = mapped_column(primary_key=True)
    dish_id: Mapped[int] = mapped_column(ForeignKey('public.dish.id', ondelete='CASCADE'), nullable=False)
    size: Mapped[str] = mapped_column(nullable=False)  # Размер/вариант блюда (например, "Маленький", "Большой")
    price: Mapped[float] = mapped_column(nullable=False)  # Цена для этого варианта


class User(Base):
    __tablename__ = 'user'
    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int]  # ID пользователя в Telegram
    telegram_name: Mapped[str] = mapped_column(nullable=True)  # Имя пользователя в Telegram
    telegram_username: Mapped[str] = mapped_column(nullable=True)  # Юзернейм в Telegram
    full_name: Mapped[str] = mapped_column(nullable=False)  # Полное имя пользователя
    is_support: Mapped[bool] = mapped_column(default=False)  # Является ли пользователь поддержкой
    is_admin: Mapped[bool] = mapped_column(default=False)  # Является ли пользователь администратором
    banned: Mapped[bool] = mapped_column(default=False)  # Забанен ли пользователь


class Order(Base):
    __tablename__ = 'orders'
    id: Mapped[int] = mapped_column(primary_key=True)  # Уникальный номер заказа
    user_id: Mapped[int] = mapped_column(ForeignKey('public.user.id'), nullable=False)  # Кто сделал заказ
    datetime: Mapped[datetime] = mapped_column(default=datetime.now())  # Когда сделан заказ


class OrderItem(Base):
    __tablename__ = 'order_items'
    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey('public.orders.id'))  # Ссылка на заказ
    dish_id: Mapped[int] = mapped_column(ForeignKey('public.dish.id'))  # Ссылка на блюдо
    quantity: Mapped[int] = mapped_column(default=1)  # Количество блюд