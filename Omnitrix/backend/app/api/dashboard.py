from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.dependencies.auth import get_current_user
from app.models.assessment import Assessment
from app.models.interview import Interview
from app.models.job import Job
from app.models.recommendation import Recommendation
from app.models.resume import Resume
from app.models.user import User

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
def get_dashboard_overview(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """Retrieve full dashboard stats and summary for candidate."""
    resume = (
        db.query(Resume)
        .filter(Resume.user_id == current_user.id)
        .order_by(Resume.created_at.desc())
        .first()
    )

    interviews = (
        db.query(Interview)
        .filter(Interview.user_id == current_user.id)
        .order_by(Interview.created_at.desc())
        .all()
    )

    assessments = (
        db.query(Assessment)
        .filter(Assessment.user_id == current_user.id)
        .order_by(Assessment.created_at.desc())
        .all()
    )

    recs = (
        db.query(Recommendation)
        .filter(Recommendation.user_id == current_user.id, Recommendation.is_read == False)
        .limit(5)
        .all()
    )

    recent_jobs = db.query(Job).filter(Job.status == "active").limit(5).all()

    completed_interviews = [i for i in interviews if i.status == "COMPLETED"]
    avg_score = (
        sum(i.score for i in completed_interviews if i.score is not None) / len(completed_interviews)
        if completed_interviews else 0.0
    )

    from app.services.badge_service import BadgeService
    from app.services.certificate_service import CertificateService
    badge_service = BadgeService()
    cert_service = CertificateService()

    badge_data = badge_service.get_user_badges_and_level(db=db, user=current_user)
    cert_data = cert_service.get_user_certificates(db=db, user=current_user)

    return {
        "candidate": {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "education": current_user.education,
            "career_goal": current_user.career_goal,
            "has_resume": resume is not None,
            "skills": resume.extracted_skills if resume else [],
        },
        "level_info": badge_data.level_info,
        "badges": badge_data.badges,
        "certificates": cert_data.certificates,
        "stats": {
            "interviews_total": len(interviews),
            "interviews_completed": len(completed_interviews),
            "assessments_total": len(assessments),
            "average_interview_score": round(avg_score, 1),
            "unread_recommendations": len(recs),
            "stars_earned": badge_data.level_info.stars_earned,
            "current_level": badge_data.level_info.current_level,
            "level_title": badge_data.level_info.level_title,
        },
        "recent_interviews": [
            {
                "id": i.id,
                "interview_type": i.interview_type,
                "status": i.status,
                "score": i.score,
                "created_at": i.created_at,
            }
            for i in interviews[:5]
        ],
        "recent_jobs": [
            {
                "id": j.id,
                "title": j.title,
                "company_id": j.company_id,
                "location": j.location,
                "salary_range": j.salary_range,
            }
            for j in recent_jobs
        ],
    }
