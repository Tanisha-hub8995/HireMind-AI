from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.database.database import SessionLocal
from app.models.user import User
from app.utils.security import ALGORITHM, SECRET_KEY


bearer_scheme = HTTPBearer(auto_error=True)


def get_db():
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()


def get_current_user(
	credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
	db: Annotated[Session, Depends(get_db)]
) -> User:
	credentials_exception = HTTPException(
		status_code=status.HTTP_401_UNAUTHORIZED,
		detail="Could not validate credentials",
		headers={"WWW-Authenticate": "Bearer"}
	)

	token = credentials.credentials
	try:
		payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
		user_id = payload.get("sub")
		if user_id is None:
			raise credentials_exception
		user_id = int(user_id)
	except (JWTError, ValueError):
		raise credentials_exception

	user = db.query(User).filter(User.id == user_id).first()
	if user is None:
		raise credentials_exception
	return user


optional_bearer_scheme = HTTPBearer(auto_error=False)


def get_optional_current_user(
	credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(optional_bearer_scheme)] = None,
	db: Annotated[Session, Depends(get_db)] = None,
) -> User | None:
	if not credentials:
		return None
	try:
		token = credentials.credentials
		payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
		user_id = payload.get("sub")
		if user_id is None:
			return None
		return db.query(User).filter(User.id == int(user_id)).first()
	except Exception:
		return None


def require_admin(
	current_user: Annotated[User, Depends(get_current_user)]
) -> User:
	if current_user.role != "admin":
		raise HTTPException(
			status_code=status.HTTP_403_FORBIDDEN,
			detail="Admin access required"
		)
	return current_user

