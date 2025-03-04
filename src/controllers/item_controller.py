# filepath: ScholarSafeBackend/controllers/item_controller.py
from fastapi import HTTPException
from ..models.item_model import Item, ItemInDB
from ..services.item_services import get_all_items, get_item_by_id, create_item, update_item, delete_item

async def read_items():
    items = await get_all_items()
    return [ItemInDB(**item, id=str(item["_id"])) for item in items]

async def read_item(item_id: str):
    item = await get_item_by_id(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return ItemInDB(**item, id=str(item["_id"]))

async def create_new_item(item: Item):
    new_item = await create_item(item)
    return ItemInDB(**new_item, id=str(new_item["_id"]))

async def update_existing_item(item_id: str, item: Item):
    result = await update_item(item_id, item)
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    updated_item = await get_item_by_id(item_id)
    return ItemInDB(**updated_item, id=str(updated_item["_id"]))

async def delete_existing_item(item_id: str):
    result = await delete_item(item_id)
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"message": "Item deleted successfully"}