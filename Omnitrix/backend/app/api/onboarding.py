from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.models.user import User
from app.schemas.onboarding import (
    OnboardingRequest,
    OnboardingResponse
)
from app.dependencies.auth import get_current_user


router = APIRouter(
    prefix="/onboarding",
    tags=["Onboarding"]
)


# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get(
    "/",
    response_model=OnboardingResponse
)
def get_onboarding(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == current_user.id).first()

    if not user:
        raise ValueError("User not found")

    return {
        "message": "Onboarding details fetched successfully",
        "user_id": user.id,
        "education": user.education,
        "experience": user.experience,
        "career_goal": user.career_goal
    }


@router.put(
    "/",
    response_model=OnboardingResponse
)
def update_onboarding(
    data: OnboardingRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == current_user.id).first()

    if not user:
        raise ValueError("User not found")

    user.education = data.education
    user.experience = data.experience
    user.career_goal = data.career_goal

    db.commit()
    db.refresh(user)

    return {
        "message": "Onboarding updated successfully",
        "user_id": user.id,
        "education": user.education,
        "experience": user.experience,
        "career_goal": user.career_goal
    }


@router.post(
    "/",
    response_model=OnboardingResponse
)
def complete_onboarding(
    data: OnboardingRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(
        User.id == current_user.id
    ).first()

    if not user:
        return {
            "message": "User not found",
            "user_id": current_user.id
        }

    user.education = data.education
    user.experience = data.experience
    user.career_goal = data.career_goal

    db.commit()
    db.refresh(user)

    return {
        "message": "Onboarding completed successfully",
        "user_id": user.id,
        "education": user.education,
        "experience": user.experience,
        "career_goal": user.career_goal
    }