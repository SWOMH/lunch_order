from pydantic import BaseModel, Field
from typing import Optional

class TelegramId(BaseModel):
    telegram_id: int = Field(ge=0, description="ID пользователя в Telegram")  # Не до конца уверен, что в телеге id не с - идут. Потом проверю

class UserSchema(TelegramId):
    full_name: str = Field(max_length=100)    

class DishOrder(BaseModel):
    dish_id: int = Field(gt=0, description="ID блюда в меню")
    count: int = Field(gt=0, description="Количество единиц блюда")
    variant_id: Optional[int | None] = Field(
        None, gt=0, description="ID варианта блюда (например, размер или добавка)"
    )


class OrderType(TelegramId):
    dishes: list[DishOrder] = Field(description="Список заказанных блюд")
    # amount: float = Field(
    #     ge=0, description="Общая сумма заказа в рублях"
    # )

