from pydantic import BaseModel, Field, EmailStr
from bson import ObjectId
from typing import List

# Request models
class ProjectCreate(BaseModel):
    project_title: str = Field(..., max_length=255)
    project_description: str
    project_pdf_link: str = Field(..., max_length=500)
    team_members: List[str] 
    year_done: int
    tech_stack: List[str]

    def to_dict(self) -> dict:
        return {
            "project_title": self.project_title,
            "project_description": self.project_description,
            "project_pdf_link": self.project_pdf_link,
            "team_members": self.team_members,
            "year_done": self.year_done,
            "tech_stack": self.tech_stack
        }