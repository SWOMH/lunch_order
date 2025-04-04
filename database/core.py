from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from database.models.lunch import Dish, DishVariant, User, Order, OrderItem


class DatabaseCore:
    def __init__(self, url_con: str, create_tables: bool = False):        
        self.engine = create_async_engine(
            url_con,
            pool_size=10, max_overflow=20
        )
        self.Session = async_sessionmaker(bind=self.engine, expire_on_commit=False)


        # if create_tables:
        #     import asyncio
        #     asyncio.run(self.create_tables())
    # async def create_tables(self):
    #     """Асинхронно создает таблицы в базе данных."""
    #     async with self.engine.begin() as conn:
    #         await conn.run_sync(Base.metadata.create_all)

