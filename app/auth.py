import os
import re
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

JWT_SECRET = os.getenv("JWT_SECRET", "local-dev-secret-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_HOURS = 24

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

PASSWORD_RULES = re.compile(
    r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[!@#$%^&*()\-_=+\[\]{};:\'",.<>/?\\|`~]).{8,}$'
)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def validate_password(password: str) -> bool:
    return bool(PASSWORD_RULES.match(password))


def create_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRE_HOURS)
    return jwt.encode({"sub": str(user_id), "exp": expire}, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> int:
    payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    return int(payload["sub"])
