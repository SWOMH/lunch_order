from database.core import DatabaseCore
from constant import CONSTANT
from functools import wraps
from typing import Callable, Coroutine, Any


class DataBaseMainConnect(DatabaseCore):
    def __init__(self):
        url_con = CONSTANT.url_connection
        super().__init__(str(url_con), create_tables=True)

    def connection(self, method: Callable[..., Coroutine[Any, Any, Any]]):
        @wraps(method)  # Сохраняем метаданные исходной функции
        async def wrapper(*args, **kwargs):
            # Открываем новую сессию
            async with self.Session() as session:
                try:
                    # Вызываем метод, передавая сессию как аргумент
                    result = await method(*args, session=session, **kwargs)
                    await session.commit()  # Фиксируем изменения, если не было ошибок
                    return result
                except Exception as e:
                    await session.rollback()  # Откатываем при ошибке
                    raise e  # Пробрасываем исключение дальше
                # Сессия автоматически закрывается благодаря async with

        return wrapper