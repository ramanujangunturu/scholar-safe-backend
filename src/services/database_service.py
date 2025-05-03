import motor.motor_asyncio
from bson import ObjectId
from dotenv import load_dotenv
from ..models.project_model import ProjectCreate  # Use relative import
import os
import aiohttp
from PyPDF2 import PdfReader
from io import BytesIO
from sentence_transformers import SentenceTransformer

# Initialize the SentenceTransformer model
model = SentenceTransformer('all-MiniLM-L6-v2')
# from ..services.project_service import generate_embedding  # Import the embedding generator

load_dotenv(override=True)

MONGO_DETAILS = os.getenv("MONGO_DETAILS")

client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_DETAILS)
database = client.scholarSafe
users_collection = database.get_collection("users")
project_collection = database.get_collection("projects")


async def generate_embedding(text: str) -> list:
    try:
        embedding = model.encode(text).tolist()
        return embedding
    except Exception as e:
        raise Exception(f"Error generating embedding: {e}")

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

async def extract_text_from_pdf(pdf_url: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(pdf_url) as response:
            if response.status == 200:
                pdf_data = await response.read()
                pdf_reader = PdfReader(BytesIO(pdf_data))
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                return text
            else:
                raise Exception(f"Failed to fetch PDF. Status code: {response.status}")

async def create_project(project: ProjectCreate) -> dict:
    project_data = project.to_dict()
    # Extract text from the PDF and add it to the project data
    try:
        pdf_description = await extract_text_from_pdf(project.project_pdf_link)
        project_data["project_pdf_description"] = pdf_description
    except Exception as e:
        raise Exception(f"Failed to extract text from PDF: {e}")
    
    # Combine project description and PDF description for embedding
    combined_description = f"{project.project_description} {project_data['project_pdf_description']}"
    try:
        project_data["project_description_embedding"] = await generate_embedding(combined_description)
    except Exception as e:
        raise Exception(f"Failed to generate embedding: {e}")
    
    # Save the project to the database
    result = await project_collection.insert_one(project_data)
    new_project = await project_collection.find_one({"_id": result.inserted_id})
    return {
        "id": str(new_project["_id"]),
        "project_title": new_project["project_title"],
        "project_description": new_project["project_description"],
        "project_pdf_link": new_project["project_pdf_link"],
        "project_pdf_description": new_project["project_pdf_description"],
        "project_description_embedding": new_project["project_description_embedding"],
        "team_members": new_project["team_members"],
        "year_done": new_project["year_done"],
        "tech_stack": new_project["tech_stack"]
    }

async def search_projects_by_title_in_db(keyword: str = "") -> list:
    try:
        query = {}
        if keyword:
            # Perform a case-insensitive regex search on the project_title field
            query = {"project_title": {"$regex": keyword, "$options": "i"}}
        
        # Fetch all matching projects
        projects_cursor = project_collection.find(query)
        projects = await projects_cursor.to_list(length=None)  # Fetch all results
        return [
            {
                "id": str(project["_id"]),
                "project_title": project["project_title"],
                "project_description": project["project_description"],
                "project_pdf_link": project["project_pdf_link"],
                "team_members": project["team_members"],
                "year_done": project["year_done"],
                "tech_stack": project["tech_stack"]
            }
            for project in projects
        ]
    except Exception as e:
        raise Exception(f"Error while searching projects: {e}")

async def fetch_all_projects_in_db() -> list:
    try:
        # Fetch all projects
        projects_cursor = project_collection.find({})
        projects = await projects_cursor.to_list(length=None)  # Fetch all results
        return [
            {
                "id": str(project["_id"]),
                "project_title": project["project_title"],
                "project_description": project["project_description"],
                "project_pdf_link": project["project_pdf_link"],
                "team_members": project["team_members"],
                "year_done": project["year_done"],
                "tech_stack": project["tech_stack"]
            }
            for project in projects
        ]
    except Exception as e:
        raise Exception(f"Error while fetching all projects: {e}")

async def fetch_projects_by_ids(project_ids: list) -> list:
    try:
        # Convert string IDs to ObjectId
        object_ids = [ObjectId(pid) for pid in project_ids]
        projects = await project_collection.find({"_id": {"$in": object_ids}}).to_list(length=len(project_ids))
        
        # Convert ObjectId to string
        return [
            {
                **project,
                "id": str(project["_id"]),  # Convert _id to string
                "_id": str(project["_id"]),  # Optional: Keep _id as string if needed
            }
            for project in projects
        ]
    except Exception as e:
        raise Exception(f"Error fetching projects by IDs: {e}")