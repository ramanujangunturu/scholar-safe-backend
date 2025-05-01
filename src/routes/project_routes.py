from fastapi import APIRouter, Query
from typing import List
from ..models.project_model import ProjectCreate
from ..controllers.project_controller import save_project, search_projects_by_title, fetch_all_projects

router = APIRouter()

@router.post("/add", response_model=dict)
async def post_project(project: ProjectCreate):
    return await save_project(project)
from typing import Optional

@router.get("/search", response_model=List[dict])
async def search_projects(
    keyword: Optional[str] = Query(None, description="Keyword to search in project titles")
):
    return await search_projects_by_title(keyword or "")

@router.get("/all", response_model=List[dict])
async def get_all_projects():
    return await fetch_all_projects()
