# filepath: ScholarSafeBackend/models/item_model.py
from pydantic import BaseModel
from typing import Union

class Item(BaseModel):
    name: str
    price: float
    is_offer: Union[bool, None] = None

class ItemInDB(Item):
    id: str