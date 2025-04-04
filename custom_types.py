from pydantic import BaseModel, Field, field_validator, HttpUrl, confloat
from typing import Optional, Literal

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

class VariantType(BaseModel):
    dish_id: int = Field(..., gt=0, description="ID блюда (положительное число)")
    size: str = Field(..., min_length=1, max_length=50, 
                     description="Размер/вариант блюда (например, 'Маленький', 'Большой' или 'С креветками', 'С курицей')")
    price: float = Field(..., gt=0, description="Цена для этого варианта (положительное число)")

    @field_validator('size')
    def validate_size(cls, v):
        if not v.strip():
            raise ValueError("Размер не может быть пустым")
        return v.strip()

class DishType(BaseModel):
    dish_name: str = Field(..., min_length=1, max_length=100, description="Название блюда")
    description: str | None = Field(None, max_length=500, description="Описание")
    price: float | None = Field(gt=0, description="Базовая цена (неотрицательное число)")
    available: bool = Field(True, description="Доступно для заказа")
    image: HttpUrl | None = Field(None, description="URL картинки блюда")
    type: Literal['Соус', 'Закуски', 'Лапша/паста', 'Основные блюда',
                  'Гарниры', 'Первые блюда', 'Салаты', 'Римские пиццы',
                  'Пицца', 'Роллы горячие', 'Роллы холодные', 'Сет',
                  'Десерты', 'Завтраки', 'Добавки', 'Фитнес меню', 'Зимнее меню',
                  'Напитки'] = Field(..., description="Тип блюда")
    stop_list: bool = Field(False, description="На стопе ли блюдо?")
    is_combo: bool = Field(False, description="Это комбо?")
    additives: bool = Field(False, description="Есть ли добавки/вариации блюда")
    variants: list[VariantType | None] = Field(default_factory=list, description="Варианты блюда")

    @field_validator('dish_name')
    def validate_dish_name(cls, v):
        if not v.strip():
            raise ValueError("Название блюда не может быть пустым")
        return v.strip()