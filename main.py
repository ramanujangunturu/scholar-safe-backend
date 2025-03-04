from fastapi import FastAPI
from fastapi import APIRouter
from src.routes.item_routes import router as item_router
from src.routes.search_routes import router as search_router
from src.routes.auth_routes import router as auth_router
app = FastAPI()

api_router = APIRouter()
api_router.include_router(item_router, prefix="/items")
api_router.include_router(search_router, prefix="/search")
api_router.include_router(auth_router, prefix="/auth")

app.include_router(api_router)

@app.get("/")
def read_root():
    return {"Hello": "World"}