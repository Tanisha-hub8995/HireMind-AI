from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.badge import BadgesResponse, UserLevelInfo
from app.services.badge_service import BadgeService

router = APIRouter(prefix="/badges", tags=["Badges & Levels"])
badge_service = BadgeService()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=BadgesResponse)
def get_user_badges(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """Retrieve all unlocked and available 1-to-5 star badges, user level, and XP."""
    return badge_service.get_user_badges_and_level(db=db, user=current_user)


@router.get("/level", response_model=UserLevelInfo)
def get_user_level_info(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db),
):
    """Retrieve current user level progress (Level 1 to 5), XP, and star count."""
    badge_data = badge_service.get_user_badges_and_level(db=db, user=current_user)
    return badge_data.level_info
