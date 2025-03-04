import motor.motor_asyncio
from bson import ObjectId
from dotenv import load_dotenv
import os

load_dotenv(override=True)

MONGO_DETAILS = os.getenv("MONGO_DETAILS")

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
database = client.scholarSafe
users_collection = database.get_collection("users")

# Helpers
def user_helper(user) -> dict:
    return {
        "id": str(user["_id"]),
        "email": user["email"],
        "username": user["username"],
        "password": user["password"]
    }

async def get_user_by_email(email: str) -> dict:
    user = await users_collection.find_one({"email": email})
    if user:
        return user_helper(user)

async def create_user(user_data: dict) -> dict:
    user = await users_collection.insert_one(user_data)
    new_user = await users_collection.find_one({"_id": user.inserted_id})
    return user_helper(new_user)