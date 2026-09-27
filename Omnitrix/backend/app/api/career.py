from typing import Annotated, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.dependencies.auth import get_current_user
from app.models.career import CareerPath
from app.models.resume import Resume
from app.models.user import User
from app.services.career_recommendations import CareerRecommendationEngine

router = APIRouter(prefix="/career", tags=["Career"])
career_engine = CareerRecommendationEngine()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/recommendations")
def get_career_recommendations(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """Generate career path recommendations based on user's extracted skills."""
    resume = (
        db.query(Resume)
        .filter(Resume.user_id == current_user.id)
        .order_by(Resume.created_at.desc())
        .first()
    )
    skills = list(resume.extracted_skills or []) if resume else ["Python", "FastAPI", "SQL"]
    recommendations = career_engine.recommend(skills)
    return {
        "user_id": current_user.id,
        "skills_detected": skills,
        "recommendations": recommendations,
    }


@router.get("/paths")
def get_career_paths(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """Get active career roadmaps for the user."""
    paths = db.query(CareerPath).filter(CareerPath.user_id == current_user.id).all()
    return [
        {
            "id": p.id,
            "target_role": p.target_role,
            "current_level": p.current_level,
            "target_level": p.target_level,
            "skills_required": p.skills_required,
            "skills_acquired": p.skills_acquired,
            "estimated_time_months": p.estimated_time_months,
            "created_at": p.created_at,
        }
        for p in paths
    ]
