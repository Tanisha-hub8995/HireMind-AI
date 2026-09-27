from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.dependencies.auth import get_current_user
from app.models.resume import Resume
from app.models.user import User
from app.services.career_recommendations import CareerRecommendationEngine


router = APIRouter(prefix="/jobs", tags=["Jobs"])
career_engine = CareerRecommendationEngine()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/recommendations")
def recommend_jobs_from_resume(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
    limit: int = 4,
):
    latest_resume = (
        db.query(Resume)
        .filter(
            Resume.user_id == current_user.id,
            Resume.processing_status == "completed",
        )
        .order_by(Resume.created_at.desc())
        .first()
    )
    if latest_resume is None:
        raise HTTPException(
            status_code=404,
            detail="Upload and analyze a resume before requesting job recommendations",
        )

    analysis = (latest_resume.payload or {}).get("analysis", {})
    candidate_skills = analysis.get("skills") or latest_resume.extracted_skills or []
    candidate_skills = [
        item.get("name") if isinstance(item, dict) else item
        for item in candidate_skills
    ]
    candidate_skills = [skill for skill in candidate_skills if skill]

    recommendations = career_engine.recommend(candidate_skills)
    return {
        "user_id": current_user.id,
        "resume_id": latest_resume.id,
        "profile": {
            "name": current_user.name,
            "skills": candidate_skills,
            "resume_summary": latest_resume.summary,
        },
        "recommendations": recommendations[: max(1, min(limit, 10))],
    }


@router.get("/")
def list_jobs(db: Session = Depends(get_db)):
    """List all active job postings with hiring company info."""
    from app.models.job import Job
    jobs = db.query(Job).filter(Job.status == "active").all()
    return [
        {
            "id": j.id,
            "title": j.title,
            "company_name": j.company.name if j.company else None,
            "company_id": j.company_id,
            "description": j.description,
            "required_skills": j.required_skills,
            "location": j.location,
            "salary_range": j.salary_range,
            "job_type": j.job_type,
            "status": j.status,
            "created_at": j.created_at,
        }
        for j in jobs
    ]


@router.get("/{job_id}")
def get_job(job_id: int, db: Session = Depends(get_db)):
    """Get detailed job description and requirements."""
    from app.models.job import Job
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "id": job.id,
        "title": job.title,
        "company_name": job.company.name if job.company else None,
        "company_id": job.company_id,
        "description": job.description,
        "required_skills": job.required_skills,
        "location": job.location,
        "salary_range": job.salary_range,
        "job_type": job.job_type,
        "status": job.status,
        "created_at": job.created_at,
    }

