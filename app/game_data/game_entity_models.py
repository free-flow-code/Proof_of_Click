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
        Возвращает строковое представление всех атрибутов предмета
        и их значений в формате `key=value`.
        """
        attrs = vars(self)
        return ', '.join(f"{key}={value}" for key, value in attrs.items())

    def get_value(self, key: str):
        """
        Получает значение указанного атрибута предмета.
        """
        attrs = vars(self)
        if key in attrs:
            return attrs[key]
        raise KeyError(f"Attribute '{key}' not found.")

    def get_all_values(self) -> dict:
        """
        Возвращает все атрибуты предмета в виде словаря.
        """
        return vars(self)


class GameBoost:
    def __init__(self, boost_name, **kwargs):
        self.name: str = boost_name
        self.titles: dict = kwargs.get("titles")
        self.descriptions: dict = kwargs.get("descriptions")
        self.properties: dict = kwargs.get("properties")
        self.usdt_price: int = kwargs.get("usdt_price")
        self.image_id: int = kwargs.get("image_id")
        self.levels: dict = kwargs.get("levels")
        self.max_levels: int = len(self.levels)

    def __str__(self):
        attrs = vars(self)
        return ', '.join(f"{key}={value}" for key, value in attrs.items())

    def get_value(self, key):
        attrs = vars(self)
        if key in attrs:
            return attrs[key]
        raise KeyError(f"Attribute '{key}' not found.")

    def get_all_values(self):
        return vars(self)


class GameRegistry:
    """
    Реестр игровых сущностей для управления добавлением, удалением и получением предметов и улучшений.

    Attributes:
        items (dict): Словарь сущностей, где ключи - названия сущностей, а значения - объекты GameItem или GameBoost.
    """
    model = None

    def __init__(self):
        self.items = {}

    def add_entity(self, key, item):
        """
        Добавляет сущность в реестр.
        """
        self.items[key] = item

    def get_entity(self, key: str) -> dict:
        """
        Получает сущность из реестра по ключу.
        """
        item = self.items.get(key)
        return item.get_all_values()

    def get_all_entities(self) -> dict:
        """
        Получает все сущности из реестра.
        """
        return self.items

    def delete_entity(self, key: str) -> None:
        """
        Удаляет сущность из реестра.
        """
        del self.items[key]


class GameItemsRegistry(GameRegistry):
    pass


class GameBoostsRegistry(GameRegistry):
    pass


items_registry = GameItemsRegistry()
boosts_registry = GameBoostsRegistry()


async def get_items_registry() -> GameItemsRegistry:
    """
    Возвращает реестр игровых предметов.

    Returns:
        GameItemsRegistry: Экземпляр реестра игрового предмета.
    """
    return items_registry


async def get_boosts_registry() -> GameBoostsRegistry:
    """
    Возвращает реестр игровых улучшений.

    Returns:
        GameBoostsRegistry: Экземпляр реестра игрового улучшения.
    """
    return boosts_registry
