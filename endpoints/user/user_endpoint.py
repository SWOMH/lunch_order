from fastapi import APIRouter
from database.bloc import database_user
from custom_types import TelegramId, UserSchema


router = APIRouter(
    prefix='/user'
)


@router.post("", tags=["user"])
async def get_user_by_telegram_id(telegram_id: TelegramId):
    return await database_user.get_user(telegram_id.telegram_id)


@router.post("/get_users", tags=["user"])
async def get_all_users(telegram_id: TelegramId):
    if await database_user.get_user_permission(telegram_id.telegram_id):
        return await database_user.get_all_users()
    else:
        return {"status": "bad",
                "detail": "permission denied"}


@router.post("/register", tags=["user"])
async def register_user(user: UserSchema):
    res = await database_user.register_user(user.telegram_id, user.full_name)
    return res
