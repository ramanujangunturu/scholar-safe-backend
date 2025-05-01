# filepath: ScholarSafeBackend/api.py
from fastapi import APIRouter
from .src.routes.item_routes import router as item_router
from .src.routes.project_routes import router as project_router

api_router = APIRouter()