from database.main_connect import DataBaseMainConnect
from database.models.lunch import DishVariant, Dish


class DataBaseDish(DataBaseMainConnect):

    def get_all_dishes_with_variants(self):
        session = self.Session()
        with session:
            query = (
                session.query(Dish, DishVariant)
                .outerjoin(DishVariant, Dish.id == DishVariant.dish_id)
                .all()
            )
            result = {}
            for dish, variant in query:
                if dish.id not in result:
                    result[dish.id] = {
                        "dish_name": dish.dish_name,
                        "description": dish.description,
                        "available": dish.available,
                        "stop_list": dish.stop_list,
                        "variants": []
                    }
                if variant:
                    result[dish.id]["variants"].append({
                        "size": variant.size,
                        "price": variant.price
                    })

            return result

    # def add_dishes_to_db(self, dishes: list):
    #     session = self.Session()
    #     with session:
    #         for dish_data in dishes:
    #             # Создаем или находим запись для блюда
    #             dish = session.query(Dish).filter_by(dish_name=dish_data["dish_name"]).first()
    #             if not dish:
    #                 dish = Dish(
    #                     dish_name=dish_data["dish_name"],
    #                     description=dish_data.get("description", ""),
    #                     available=bool(dish_data.get("available", True)),
    #                     price=dish_data.get("price") if dish_data.get("price") != '' else None,
    #                     image=dish_data.get("image", ""),
    #                     type=dish_data.get("type", ""),
    #                     stop_list=False
    #                 )
    #                 session.add(dish)
    #                 session.flush()  # Сохраняем, чтобы получить ID блюда
    #
    #             # Если есть варианты, добавляем их
    #             variants = dish_data.get("variants", [])
    #             for variant_data in variants:
    #                 size = variant_data.get("size")
    #                 price = variant_data.get("price")
    #
    #                 if size and price:
    #                     # Проверяем, есть ли уже такой вариант для блюда
    #                     variant = session.query(DishVariant).filter_by(dish_id=dish.id, size=size).first()
    #                     if not variant:
    #                         variant = DishVariant(dish_id=dish.id, size=size, price=price)
    #                         session.add(variant)
    #
    #             # Если у блюда нет вариантов, добавляем его цену в качестве единственного варианта
    #             # if not variants and dish_data.get("price"):
    #             #     price_variant = DishVariant(
    #             #         dish_id=dish.id,
    #             #         size="Стандарт",
    #             #         price=dish_data["price"]
    #             #     )
    #             #     session.add(price_variant)
    #
    #         session.commit()  # Сохраняем изменения