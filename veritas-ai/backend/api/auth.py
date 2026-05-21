"""
VERITAS AI — Auth API Routes
"""
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status

from core.config import settings
from core.security import (
    USERS_DB,
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)
from models.schemas import LoginRequest, TokenResponse, UserResponse

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """Authenticate user and return JWT token."""
    user = USERS_DB.get(request.email)
    if not user or not verify_password(request.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    token = create_access_token(
        data={"sub": user["email"], "role": user["role"]},
        expires_delta=timedelta(minutes=settings.JWT_EXPIRE_MINUTES),
    )
    user_response = {k: v for k, v in user.items() if k != "hashed_password"}
    return TokenResponse(access_token=token, user=user_response)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    """Get current authenticated user."""
    return UserResponse(
        id=current_user["id"],
        email=current_user["email"],
        name=current_user["name"],
        role=current_user["role"],
        created_at=current_user["created_at"],
    )


@router.post("/logout")
async def logout():
    """Logout (client-side token deletion)."""
    return {"message": "Logged out successfully"}
