from database.core import DatabaseCore
import os
from dotenv import load_dotenv
from constant import CONSTANT

load_dotenv()


class DataBaseMainConnect(DatabaseCore):
    def __init__(self):
        user = CONSTANT.POSTGRES_USER
        password = CONSTANT.POSTGRES_PASSWORD
        host = CONSTANT.POSTGRES_HOST
        port = CONSTANT.POSTGRES_PORT
        database = CONSTANT.POSTGRES_DB_NAME

        if CONSTANT.dev:
            url_con = CONSTANT.dev_database
        else:
            if not all([user, password, host, port, database]):
                raise ValueError("One or more environment variables are not set.")
            url_con = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"

        super().__init__(str(url_con), create_tables=True)
