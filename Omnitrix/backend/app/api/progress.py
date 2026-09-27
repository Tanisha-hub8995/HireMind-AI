from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.dependencies.auth import get_current_user
from app.models.assessment import Assessment
from app.models.interview import Interview
from app.models.progress import UserProgress
from app.models.user import User

router = APIRouter(prefix="/progress", tags=["Progress"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
def get_user_progress(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """Retrieve learning analytics, metrics and performance history for the user."""
    records = (
        db.query(UserProgress)
        .filter(UserProgress.user_id == current_user.id)
        .order_by(UserProgress.recorded_at.desc())
        .all()
    )

    interviews = (
        db.query(Interview)
        .filter(Interview.user_id == current_user.id, Interview.status == "COMPLETED")
        .all()
    )
    assessments = (
        db.query(Assessment)
        .filter(Assessment.user_id == current_user.id, Assessment.status.in_(["COMPLETED", "completed"]))
        .all()
    )

    avg_interview = (
        sum(i.score for i in interviews if i.score is not None) / len(interviews)
        if interviews else 0.0
    )
    avg_assessment = (
        sum(a.percentage for a in assessments if a.percentage is not None) / len(assessments)
        if assessments else 0.0
    )

    from app.services.badge_service import BadgeService
    from app.services.certificate_service import CertificateService
    badge_service = BadgeService()
    cert_service = CertificateService()

    badge_data = badge_service.get_user_badges_and_level(db=db, user=current_user)
    cert_data = cert_service.get_user_certificates(db=db, user=current_user)

    return {
        "user_id": current_user.id,
        "interviews_completed": len(interviews),
        "assessments_completed": len(assessments),
        "average_interview_score": round(avg_interview, 1),
        "average_assessment_score": round(avg_assessment, 1),
        "current_level": badge_data.level_info.current_level,
        "level_title": badge_data.level_info.level_title,
        "stars_earned": badge_data.level_info.stars_earned,
        "xp": badge_data.level_info.xp,
        "certificates_count": cert_data.total_certificates,
        "recent_metrics": [
            {
                "category": r.category,
                "metric_name": r.metric_name,
                "value": r.value,
                "recorded_at": r.recorded_at,
            }
            for r in records[:20]
        ],
    }
