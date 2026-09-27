from pwdlib import PasswordHash
from jose import jwt
from datetime import datetime, timedelta, timezone


# Password hashing
password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    return password_hash.verify(
        plain_password,
        hashed_password
    )


# JWT settings
SECRET_KEY = "change-this-secret-key-later"
ALGORITHM = "HS256"


def create_access_token(
    user_id: int,
    expires_minutes: int = 60
) -> str:

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=expires_minutes
    )

    payload = {
        "sub": str(user_id),
        "exp": expire
    }

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token