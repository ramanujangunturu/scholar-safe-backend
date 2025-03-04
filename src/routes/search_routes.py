from fastapi import APIRouter, HTTPException
from typing import List, Optional
from ..services.search_service import search_projects

router = APIRouter()

@router.get("/search", response_model=List[dict])
async def search(query: str):
    try:
        results = search_projects(query )
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))