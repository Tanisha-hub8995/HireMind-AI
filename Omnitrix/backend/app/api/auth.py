from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.models.user import User
from app.schemas.user import (
    UserSignup,
    UserResponse,
    TokenResponse,
    UserUpdate
)
from app.utils.security import (
    hash_password,
    verify_password,
    create_access_token
)
from app.dependencies.auth import get_current_user, require_admin


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


@router.post(
    "/signup",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def signup(
    user_data: UserSignup,
    db: Session = Depends(get_db)
):

    # Check if email already exists
    existing_user = (
        db.query(User)
        .filter(User.email == user_data.email)
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # Hash password
    hashed_password = hash_password(
        user_data.password
    )

    # Create user
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=hashed_password,
        role=user_data.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.get("/users", response_model=list[UserResponse])
def get_all_users(
    _: Annotated[User, Depends(require_admin)],
    db: Session = Depends(get_db)
):
    return db.query(User).order_by(User.id).all()


@router.patch("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    user_data: UserUpdate,
    _: Annotated[User, Depends(require_admin)],
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if user_data.email is not None:
        email_owner = (
            db.query(User)
            .filter(User.email == user_data.email, User.id != user_id)
            .first()
        )
        if email_owner:
            raise HTTPException(status_code=400, detail="Email already registered")
        user.email = user_data.email

    if user_data.name is not None:
        user.name = user_data.name
    if user_data.password is not None:
        user.password_hash = hash_password(user_data.password)
    if user_data.role is not None:
        user.role = user_data.role

    db.commit()
    db.refresh(user)
    return user
@router.post(
    "/login",
    response_model=TokenResponse
)
def login(
    user_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
):

    # Find user
    user = (
        db.query(User)
        .filter(User.email == user_data.username)
        .first()
    )

    # User doesn't exist
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Check password
    if not verify_password(
        user_data.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    # Create JWT
    access_token = create_access_token(
        user.id
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get("/me", response_model=UserResponse)
def get_me(
    current_user: Annotated[User, Depends(get_current_user)]
):
    return current_user


@router.get("/admin", response_model=UserResponse)
def get_admin_area(
    current_user: Annotated[User, Depends(require_admin)]
):
    return current_user