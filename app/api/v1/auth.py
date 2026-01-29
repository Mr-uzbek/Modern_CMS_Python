"""
Authentication API endpoints
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import create_access_token, create_refresh_token, verify_token
from app.core.config import settings
from app.schemas.user import (
    LoginRequest, TokenResponse, RegisterRequest, RefreshTokenRequest,
    UserResponse, PasswordResetRequest, PasswordResetConfirm
)
from app.schemas.common import ResponseMessage
from app.services.user import UserService


router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_client_ip(request: Request) -> str:
    """Get client IP from request"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    User login
    
    Returns access and refresh tokens on successful authentication.
    """
    service = UserService(db)
    user = await service.authenticate(data.username, data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    
    # Update last login
    await service.update_last_login(user, get_client_ip(request))
    
    # Create tokens
    token_data = {"sub": str(user.id), "username": user.username}
    
    expires_delta = timedelta(
        days=7 if data.remember_me else 0,
        minutes=0 if data.remember_me else settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    
    access_token = create_access_token(token_data, expires_delta)
    refresh_token = create_refresh_token(token_data)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=int(expires_delta.total_seconds()) if data.remember_me else settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    data: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Register new user
    
    Creates a new user account with default user group.
    """
    service = UserService(db)
    
    # Check if username exists
    existing = await service.get_by_username(data.username)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )
    
    # Check if email exists
    existing = await service.get_by_email(data.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Create user with default group (id=2 is regular User)
    user = await service.create(data, group_id=2)
    
    return user


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Refresh access token
    
    Use the refresh token to get a new access token.
    """
    payload = verify_token(data.refresh_token, token_type="refresh")
    
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
    
    user_id = payload.get("sub")
    service = UserService(db)
    user = await service.get_by_id(int(user_id))
    
    if not user or not user.is_active or user.is_banned:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )
    
    token_data = {"sub": str(user.id), "username": user.username}
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/password/reset", response_model=ResponseMessage)
async def request_password_reset(
    data: PasswordResetRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Request password reset
    
    Sends password reset link to user's email.
    """
    service = UserService(db)
    user = await service.get_by_email(data.email)
    
    # Always return success to prevent email enumeration
    if user:
        # TODO: Send password reset email
        pass
    
    return ResponseMessage(
        message="If the email exists, you will receive a password reset link",
    )


@router.post("/password/confirm", response_model=ResponseMessage)
async def confirm_password_reset(
    data: PasswordResetConfirm,
    db: AsyncSession = Depends(get_db),
):
    """
    Confirm password reset
    
    Reset password using the token from email.
    """
    # TODO: Implement token verification and password reset
    
    return ResponseMessage(
        message="Password has been reset successfully",
    )


@router.post("/logout", response_model=ResponseMessage)
async def logout():
    """
    Logout user
    
    Client should discard the tokens.
    """
    return ResponseMessage(
        message="Logged out successfully",
    )
