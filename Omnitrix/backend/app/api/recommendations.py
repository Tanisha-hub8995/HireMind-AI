from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.dependencies.auth import get_current_user
from app.models.recommendation import Recommendation
from app.models.resource import LearningResource
from app.models.user import User

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
def get_recommendations(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """Retrieve personalized practice, skill improvement and learning recommendations."""
    recs = (
        db.query(Recommendation)
        .filter(Recommendation.user_id == current_user.id)
        .order_by(Recommendation.created_at.desc())
        .all()
    )

    resources = db.query(LearningResource).limit(10).all()

    return {
        "recommendations": [
            {
                "id": r.id,
                "rec_type": r.rec_type,
                "title": r.title,
                "description": r.description,
                "score": r.score,
                "payload": r.payload,
                "is_read": r.is_read,
                "created_at": r.created_at,
            }
            for r in recs
        ],
        "suggested_resources": [
            {
                "id": res.id,
                "skill_name": res.skill_name,
                "title": res.title,
                "url": res.url,
                "description": res.description,
                "resource_type": res.resource_type,
                "difficulty": res.difficulty,
            }
            for res in resources
        ],
    }


@router.patch("/{rec_id}/read")
def mark_recommendation_read(
    rec_id: int,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """Mark a recommendation as read."""
    rec = db.query(Recommendation).filter(
        Recommendation.id == rec_id,
        Recommendation.user_id == current_user.id,
    ).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    rec.is_read = True
    db.commit()
    return {"message": "Recommendation marked as read", "id": rec.id}
