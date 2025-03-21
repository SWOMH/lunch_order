from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from .base import Base
from database.models.lunch import Dish, DishVariant, User, Order, OrderItem


class DatabaseCore:
    def __init__(self, url_con: str, create_tables: bool = False):
        self.engine = create_engine(
            url_con,
            pool_size=10, max_overflow=20
        )
        if url_con.startswith("sqlite"):
            Dish.__table__.schema = None
            DishVariant.__table__.schema = None
            User.__table__.schema = None
            Order.__table__.schema = None
            OrderItem.__table__.schema = None

        if create_tables:
            Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
