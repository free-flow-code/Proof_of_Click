import json

from app.utils.logger_init import logger
from app.config import settings
from app.redis_init import get_redis
from app.improvements.dao import ImprovementsDAO


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


async def get_items_quantity_from_db(item_keys: list[str]) -> dict:
    """
    Получает количество записей из таблицы игровых предметов по ключам в списке.

    Args:
        item_keys (list): Список ключей.

    Returns:
        dict: Словарь вида <ключ>: <количество записей>
    """
    items_data = {}
    for item_key in item_keys:
        item_quantity = await ImprovementsDAO.count_records_by_key(name=item_key)
        items_data[item_key] = item_quantity
    return items_data


async def set_items_quantity_in_redis(items_data: dict, redis_client):
    """
    Устанавливает начальное количество для игрового предмета в Redis.

    Args:
        items_data (dict): Словарь с названием предмета и количеством.
        redis_client: Асинхронный клиент Redis для взаимодействия с базой данных.
    """
    async with redis_client.pipeline() as pipe:
        for item_name, quantity in items_data.items():
            await pipe.hset(f"item_quantities:{settings.REDIS_NODE_TAG_1}", item_name, quantity)
        await pipe.execute()


async def create_game_items() -> None:
    """
    Создаёт игровые предметы на основе данных из JSON-файла и добавляет их в реестр.

    Returns:
        None
    """
    logger.info("Creating game items has been launched...")
    redis_client = await get_redis()
    with open("app/game_data/game_items.json", "r", encoding="utf-8") as file:
        items = json.loads(file.read())
        item_keys = []
        for game_item in items:
            for item_key, item_details in game_item.items():
                item = GameItem(item_key, **item_details)
                registry.add_item(item_key, item)
                item_keys.append(item_key)
        items_data = await get_items_quantity_from_db(item_keys)
        await set_items_quantity_in_redis(items_data, redis_client)
    logger.info("Game items create successful.")


async def get_items_registry() -> GameItemsRegistry:
    """
    Возвращает реестр игровых предметов.

    Returns:
        GameItemsRegistry: Экземпляр реестра игровых предметов.
    """
    return registry
