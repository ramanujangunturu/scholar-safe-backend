# filepath: ScholarSafeBackend/api.py
from fastapi import APIRouter
from .src.routes.item_routes import router as item_router

api_router = APIRouter()
api_router.include_router(item_router, prefix="/items")