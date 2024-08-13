import json
import logging


class GameItem:
    def __init__(self, key, **kwargs):
        self.key = key
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __str__(self):
        attrs = vars(self)
        return ', '.join(f"{key}={value}" for key, value in attrs.items())


class GameItemsRegistry:
    def __init__(self):
        self.items = {}

    def add_item(self, key, item):
        self.items[key] = item

    def get_item(self, key):
        return self.items.get(key)

    def get_all_items(self):
        return self.items


registry = GameItemsRegistry()


async def create_game_items():
    """Создает объекты игровых предметов из json файла."""
    with open("app/game_items.json", "r", encoding="utf-8") as file:
        items = json.loads(file.read())
        for game_item in items:
            for item_key, item_details in game_item.items():
                item = GameItem(item_key, **item_details)
                registry.add_item(item_key, item)
    logging.info("Game items create successful")


async def get_registry():
    return registry
