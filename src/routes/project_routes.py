from fastapi import APIRouter, Query
from typing import List, Optional
from pydantic import BaseModel, HttpUrl
from ..models.project_model import ProjectCreate
from ..controllers.project_controller import (
    save_project,
    search_projects_by_title,
    fetch_all_projects,
    search_projects_by_description,
)

router = APIRouter()

class SimilaritySearchRequest(BaseModel):
    description: Optional[str] = None
    pdf_url: Optional[str] = None
    top_k: int = 5

@router.post("/add", response_model=dict)
async def post_project(project: ProjectCreate):
    return await save_project(project)

@router.get("/search", response_model=List[dict])
async def search_projects(
    keyword: Optional[str] = Query(None, description="Keyword to search in project titles")
):
    return await search_projects_by_title(keyword or "")

@router.get("/all", response_model=List[dict])
async def get_all_projects():
    return await fetch_all_projects()

@router.post("/similarity-search", response_model=List[dict])
async def similarity_search(request: SimilaritySearchRequest):
    return await search_projects_by_description(
        description=request.description or "",
        top_k=request.top_k,
        pdf_url=request.pdf_url,
    )
