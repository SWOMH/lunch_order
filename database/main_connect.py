from database.core import DatabaseCore
from constant import CONSTANT


class DataBaseMainConnect(DatabaseCore):
    def __init__(self):
        # user = CONSTANT.POSTGRES_USER_DEV if CONSTANT.dev else CONSTANT.POSTGRES_USER
        # password = CONSTANT.POSTGRES_PASSWORD_DEV if CONSTANT.dev else CONSTANT.POSTGRES_PASSWORD
        # host = CONSTANT.POSTGRES_HOST_DEV if CONSTANT.dev else CONSTANT.POSTGRES_HOST
        # port = CONSTANT.POSTGRES_PORT_DEV if CONSTANT.dev else CONSTANT.POSTGRES_PORT
        # database = CONSTANT.POSTGRES_DB_NAME_DEV if CONSTANT.dev else CONSTANT.POSTGRES_DB_NAME
        url_con = CONSTANT.url_connection
        # if not all([user, password, host, port, database]):
        #     raise ValueError("One or more environment variables are not set.")
        # url_con = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"

        super().__init__(str(url_con), create_tables=True)

    def connection(self, method):
        async def wrapper(*args, **kwargs):
            async with self.Session() as session:
                try:
                    # Явно не открываем транзакции, так как они уже есть в контексте
                    return await method(*args, session=session, **kwargs)
                except Exception as e:
                    await session.rollback()  # Откатываем сессию при ошибке
                    raise e  # Поднимаем исключение дальше
                finally:
                    await session.close()  # Закрываем сессию

        return wrapper