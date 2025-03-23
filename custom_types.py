from pydantic import BaseModel, Field


class UserSchema(BaseModel):
    full_name: str
    telegram_id: int = Field(ge=0)  # Не до конца уверен, что в телеге id не с - идут. Потом проверю


