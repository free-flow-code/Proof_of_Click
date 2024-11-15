import json
import logging
from fastapi import Depends
from app.redis_init import get_redis


class GameItem:
    """
    Класс, представляющий игровой предмет с произвольными атрибутами.

    Args:
        key (str): Ключ для идентификации предмета.
        **kwargs: Произвольные атрибуты и значения, определяющие свойства предмета.

    Attributes:
        key (str): Ключ предмета.
        **attrs: Дополнительные атрибуты предмета, переданные через kwargs.
    """
    def __init__(self, key, **kwargs):
        self.key = key
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self):
        """
        Возвращает строковое представление всех атрибутов предмета.

        Returns:
            str: Строка, содержащая все атрибуты и их значения в формате `key=value`.
        """
        attrs = vars(self)
        return ', '.join(f"{key}={value}" for key, value in attrs.items())

    def get_value(self, key):
        """
        Получает значение указанного атрибута предмета.

        Args:
            key (str): Название атрибута.

        Returns:
            any: Значение атрибута.
        """
        attrs = vars(self)
        return attrs[key]

    def get_all_values(self):
        """
        Возвращает все атрибуты предмета в виде словаря.

        Returns:
            dict: Словарь атрибутов и их значений.
        """
        return vars(self)


class GameItemsRegistry:
    """
    Реестр игровых предметов для управления добавлением, удалением и получением предметов.

    Attributes:
        items (dict): Словарь предметов, где ключи - идентификаторы предметов, а значения - объекты GameItem.
    """
    def __init__(self):
        self.items = {}

    def add_item(self, key, item):
        """
        Добавляет предмет в реестр.

        Args:
            key (str): Ключ предмета.
            item (GameItem): Объект предмета для добавления.
        """
        self.items[key] = item

    def get_item(self, key):
        """
        Получает предмет из реестра по ключу.

        Args:
            key (str): Ключ предмета.

        Returns:
            GameItem | None: Предмет, если он существует в реестре, иначе None.
        """
        return self.items.get(key)

    def get_all_items(self):
        """
        Возвращает все предметы из реестра.

        Returns:
            dict: Словарь всех предметов.
        """
        return self.items

    def delete_item(self, key):
        """
        Удаляет предмет из реестра по ключу.

        Args:
            key (str): Ключ предмета для удаления.
        """
        del self.items[key]


registry = GameItemsRegistry()


async def set_items_quantity(item_keys: list, redis_client):
    """
    Устанавливает начальное количество для игрового предмета в Redis.

    Args:
        item_keys (list): Список ключей предметов.
        redis_client: Асинхронный клиент Redis для взаимодействия с базой данных.
    """
    async with redis_client.pipeline() as pipe:
        for key in item_keys:
            await pipe.hset("item_quantities", key, 0)
        await pipe.execute()


async def create_game_items(redis_client):
    """
    Создаёт игровые предметы на основе данных из JSON-файла и добавляет их в реестр.

    Args:
        redis_client: Клиент Redis для взаимодействия с базой данных.

    Returns:
        None
    """
    with open("app/game_data/game_items.json", "r", encoding="utf-8") as file:
        items = json.loads(file.read())
        item_keys = []
        for game_item in items:
            for item_key, item_details in game_item.items():
                item = GameItem(item_key, **item_details)
                registry.add_item(item_key, item)
                item_keys.append(item_key)
        await set_items_quantity(item_keys, redis_client)
    logging.info("Game items create successful")


async def get_items_registry():
    """
    Возвращает реестр игровых предметов.

    Returns:
        GameItemsRegistry: Экземпляр реестра игровых предметов.
    """
    return registry
