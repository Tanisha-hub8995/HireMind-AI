from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ExtractedSkill(BaseModel):
    model_config = ConfigDict(extra="ignore")

    name: str
    category: str | None = None
    evidence: str | None = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class ResumeAnalysis(BaseModel):
    model_config = ConfigDict(extra="ignore")

    skills: list[ExtractedSkill] = Field(default_factory=list)
    education: list[dict[str, Any]] = Field(default_factory=list)
    experience: list[dict[str, Any]] = Field(default_factory=list)
    internships: list[dict[str, Any]] = Field(default_factory=list)
    projects: list[dict[str, Any]] = Field(default_factory=list)
    certifications: list[dict[str, Any]] = Field(default_factory=list)
    achievements: list[dict[str, Any]] = Field(default_factory=list)
    suggested_roles: list[str] = Field(default_factory=list)
    domains: list[str] = Field(default_factory=list)


class ResumeSummary(BaseModel):
    id: int
    user_id: int
    original_filename: str | None
    processing_status: str
    sections_detected: int
    skills_extracted: int
    analysis: dict[str, Any]


class ResumeGenerateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    choice: str = Field(
        min_length=1,
        max_length=2000,
        description="Career goal, preferred role, skills, education, and experience provided by the user.",
    )


class GeneratedResume(BaseModel):
    name: str
    headline: str | None = None
    summary: str | None = None
    skills: list[str] = Field(default_factory=list)
    experience: list[dict[str, Any]] = Field(default_factory=list)
    projects: list[dict[str, Any]] = Field(default_factory=list)
    education: list[dict[str, Any]] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    achievements: list[str] = Field(default_factory=list)
    domains: list[str] = Field(default_factory=list)
    formatted_resume: str
