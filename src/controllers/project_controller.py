from fastapi import APIRouter, HTTPException
from bson import ObjectId
from ..models.project_model import ProjectCreate
from ..services.database_service import (
    create_project,
    project_collection,
    search_projects_by_title_in_db,
    fetch_all_projects_in_db,
    fetch_projects_by_ids,
    extract_text_from_pdf,  # Use the function from database_service
)
from ..services.project_service import search_projects_by_description as search_service

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

async def search_projects_by_description(description: str, top_k: int, pdf_url: str):
    try:
        # Initialize combined description
        combined_description = description.strip()

        # If a PDF URL is provided, extract text from the PDF
        if pdf_url:
            pdf_text = await extract_text_from_pdf(pdf_url)
            if pdf_text:
                combined_description += f" {pdf_text.strip()}"

        # Validate that at least one description source is provided
        if not combined_description.strip():
            raise HTTPException(status_code=400, detail="Both description and PDF URL cannot be empty")
        print(combined_description)
        # Perform similarity search to get top-k project IDs
        similar_projects = await search_service(combined_description, top_k)
        project_ids = [result["project_id"] for result in similar_projects]

        # Fetch projects from the database using the IDs
        projects = await fetch_projects_by_ids(project_ids)
        if not projects:
            raise HTTPException(status_code=404, detail="No projects found")

        return projects
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
