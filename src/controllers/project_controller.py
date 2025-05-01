from fastapi import APIRouter, HTTPException
from bson import ObjectId
from ..models.project_model import ProjectCreate
from ..services.database_service import create_project, project_collection, search_projects_by_title_in_db, fetch_all_projects_in_db

router = APIRouter()

async def save_project(project: ProjectCreate):
    try:
        new_project = await create_project(project)
        return {"message": "Project created successfully", "project": new_project}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def search_projects_by_title(keyword: str = ""):
    try:
        projects = await search_projects_by_title_in_db(keyword)
        if not projects:
            raise HTTPException(status_code=404, detail="No projects found")
        return projects
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def fetch_all_projects():
    try:
        projects = await fetch_all_projects_in_db()
        if not projects:
            raise HTTPException(status_code=404, detail="No projects found")
        return projects
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
