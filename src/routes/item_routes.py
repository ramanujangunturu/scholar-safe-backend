# filepath: ScholarSafeBackend/routes/item_routes.py
from fastapi import APIRouter
from typing import List
from ..models.item_model import Item, ItemInDB
from ..controllers.item_controller import read_items, read_item, create_new_item, update_existing_item, delete_existing_item

router = APIRouter()

@router.get("/", response_model=List[ItemInDB])
async def get_items():
    return await read_items()

@router.get("/{item_id}", response_model=ItemInDB)
async def get_item(item_id: str):
    return await read_item(item_id)

@router.post("/", response_model=ItemInDB)
async def post_item(item: Item):
    return await create_new_item(item)

@router.put("/{item_id}", response_model=ItemInDB)
async def put_item(item_id: str, item: Item):
    return await update_existing_item(item_id, item)

@router.delete("/{item_id}")
async def delete_item(item_id: str):
    return await delete_existing_item(item_id)