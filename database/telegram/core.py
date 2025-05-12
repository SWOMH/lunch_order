from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy import create_engine


class Base(DeclarativeBase):
    __abstract__ = True
    __table_args__ = {'schema': 'public'}


class DatabaseCore:
    def __init__(self, url_con: str):
        self.engine = create_engine(
            url_con,
            pool_size=10, max_overflow=20
        )
        self.Session = sessionmaker(bind=self.engine)
