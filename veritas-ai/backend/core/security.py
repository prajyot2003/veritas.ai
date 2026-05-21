"""
VERITAS AI — Security: JWT + RBAC + Password Hashing
"""
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

from core.config import settings

# ── Password Hashing ─────────────────────────────────────────
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ── Bearer Token ─────────────────────────────────────────────
security = HTTPBearer()

# ── In-Memory User Store (seeded at startup) ─────────────────
USERS_DB: dict = {}


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    payload = decode_token(credentials.credentials)
    email = payload.get("sub")
    if email is None or email not in USERS_DB:
        raise HTTPException(status_code=401, detail="User not found")
    return USERS_DB[email]


def require_role(*roles: str):
    def checker(user: dict = Depends(get_current_user)) -> dict:
        if user.get("role") not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires role: {roles}",
            )
        return user
    return checker


def seed_users():
    """Seed demo users at startup."""
    USERS_DB["admin@veritas.ai"] = {
        "id": "usr_001",
        "email": "admin@veritas.ai",
        "name": "Admin User",
        "role": "admin",
        "hashed_password": get_password_hash(settings.DEMO_ADMIN_PASSWORD),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    USERS_DB["analyst@veritas.ai"] = {
        "id": "usr_002",
        "email": "analyst@veritas.ai",
        "name": "Analyst User",
        "role": "analyst",
        "hashed_password": get_password_hash(settings.DEMO_ANALYST_PASSWORD),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    USERS_DB["viewer@veritas.ai"] = {
        "id": "usr_003",
        "email": "viewer@veritas.ai",
        "name": "Viewer User",
        "role": "viewer",
        "hashed_password": get_password_hash("viewer123"),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
