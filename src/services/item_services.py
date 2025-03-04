# filepath: ScholarSafeBackend/services/item_service.py
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from ..models.item_model import Item

client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client.mydatabase
collection = db.items

async def get_all_items():
    items = await collection.find().to_list(100)
    return items

async def get_item_by_id(item_id: str):
    item = await collection.find_one({"_id": ObjectId(item_id)})
    return item

async def create_item(item: Item):
    result = await collection.insert_one(item.model_dump())
    new_item = await collection.find_one({"_id": result.inserted_id})
    return new_item

async def update_item(item_id: str, item: Item):
    result = await collection.update_one({"_id": ObjectId(item_id)}, {"$set": item.model_dump()})
    return result

async def delete_item(item_id: str):
    result = await collection.delete_one({"_id": ObjectId(item_id)})
    return result