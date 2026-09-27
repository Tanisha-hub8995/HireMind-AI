from typing import List, Optional
from pydantic import BaseModel, ConfigDict


class JobBase(BaseModel):
    title: str
    description: Optional[str] = None
    required_skills: Optional[List[str]] = None
    location: Optional[str] = None
    salary_range: Optional[str] = None
    job_type: Optional[str] = None
    status: Optional[str] = "active"


class JobCreate(JobBase):
    company_id: Optional[int] = None


class JobResponse(JobBase):
    id: int
    company_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
