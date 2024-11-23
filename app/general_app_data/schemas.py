from typing import Dict, Tuple
from pydantic import BaseModel, RootModel


class SBoost(BaseModel):
    """
    levels - словарь, где ключи — уровни (str),
    значения — массив из двух элементов (Tuple):
    цена в игровой валюте и значение усиливаемого свойства.
    """
    titles: Dict[str, str]
    descriptions: Dict[str, str]
    properties: Dict[str, str]
    usdt_price: float
    image_id: int
    levels: Dict[str, Tuple[float, float]]


class SBoostsFile(RootModel[Dict[str, SBoost]]):
    """Модель для файла boosts.json."""


class SGameItem(BaseModel):
    titles: Dict[str, str]
    descriptions: Dict[str, str]
    drop_chance: float
    maximum_amount: int
    image_id: int


class SGameItemsFile(RootModel[Dict[str, SGameItem]]):
    """Модель для файла game_items.json"""
