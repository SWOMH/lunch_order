from sqlalchemy import ForeignKey, text, Integer, DateTime, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Annotated
from ..base import Base

intpk = Annotated[int, mapped_column(primary_key=True)]

# TABLE REVENUE =============================================>


class Dish(Base):
    __tablename__ = 'dish'
    id: Mapped[intpk]
    _id: Mapped[str] = mapped_column(nullable=True)  # Сервисный id блюда
    dish_name: Mapped[str] = mapped_column(nullable=False)  # Блюдо
    description: Mapped[str | None] = mapped_column(nullable=True)  # Описание
    price: Mapped[float | None] = mapped_column(nullable=True) # Цена
    available: Mapped[bool] = mapped_column(default=True, nullable=False)  # Доступно для заказа
    image: Mapped[str | None] = mapped_column(nullable=True) # Картинка блюда
    type: Mapped[str] = mapped_column(nullable=False)  # Тип блюда
    stop_list: Mapped[bool] = mapped_column(default=False)  # На стопе ли блюдо?
    is_combo: Mapped[bool] = mapped_column(default=False, nullable=False)  # Это комбо?
    additives: Mapped[bool] = mapped_column(default=False, nullable=False)  # Есть ли добавки/вариации блюда

    dish_variants = relationship("DishVariant", back_populates='dish')


class DishVariant(Base):
    __tablename__ = 'dish_variants'
    id: Mapped[intpk]
    dish_id: Mapped[int] = mapped_column(ForeignKey('public.dish.id', ondelete='CASCADE'), nullable=False)
    size: Mapped[str] = mapped_column(nullable=False)  # Размер/вариант блюда (например, "Маленький", "Большой")
    price: Mapped[float] = mapped_column(nullable=False)  # Цена для этого варианта

    dish = relationship("Dish", back_populates='dish_variants')


class User(Base):
    __tablename__ = 'users'
    id: Mapped[intpk]
    telegram_id: Mapped[int] = mapped_column(unique=True)  # ID пользователя в Telegram
    telegram_name: Mapped[str] = mapped_column(nullable=True)  # Имя пользователя в Telegram
    telegram_username: Mapped[str] = mapped_column(nullable=True)  # Юзернейм в Telegram
    full_name: Mapped[str] = mapped_column(nullable=False)  # Полное имя пользователя
    is_support: Mapped[bool] = mapped_column(default=False)  # Является ли пользователь поддержкой
    is_admin: Mapped[bool] = mapped_column(default=False)  # Является ли пользователь администратором
    banned: Mapped[bool] = mapped_column(default=False)  # Забанен ли пользователь

    order = relationship("Order", back_populates='user')


class Order(Base):
    __tablename__ = 'orders'
    
    id = mapped_column(Integer, primary_key=True)
    user_id = mapped_column(Integer, ForeignKey('public.users.id', ondelete='CASCADE'), nullable=False)
    datetime = mapped_column(DateTime, server_default=text("TIMEZONE('utc', now())"), nullable=False)

    user = relationship("User", back_populates="order")
    order_items = relationship("OrderItem", back_populates='order', cascade='all, delete-orphan')


class OrderItem(Base):
    __tablename__ = 'order_items'
    
    id = mapped_column(Integer, primary_key=True)
    order_id = mapped_column(Integer, ForeignKey('public.orders.id', ondelete='CASCADE'), nullable=False)
    dish_id = mapped_column(Integer, ForeignKey('public.dish.id', ondelete='CASCADE'), nullable=False)
    quantity = mapped_column(Integer, default=1)

    order = relationship("Order", back_populates='order_items')

