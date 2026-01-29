"""
User API endpoints
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.schemas.user import (
    UserResponse, UserProfileResponse, UserUpdate, UserPasswordChange,
    UserListResponse, UserGroupResponse
)
from app.schemas.common import ResponseMessage
from app.api.deps import get_current_user, get_admin_user
from app.services.user import UserService, UserGroupService


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserProfileResponse)
async def get_current_user_profile(
    user: User = Depends(get_current_user),
):
    """
    Get current user profile
    
    Returns the authenticated user's profile.
    """
    return user


@router.patch("/me", response_model=UserResponse)
async def update_current_user_profile(
    data: UserUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update current user profile
    
    Update the authenticated user's profile information.
    """
    service = UserService(db)
    updated_user = await service.update(user, data)
    return updated_user


@router.post("/me/password", response_model=ResponseMessage)
async def change_password(
    data: UserPasswordChange,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Change password
    
    Change the authenticated user's password.
    """
    service = UserService(db)
    success = await service.change_password(
        user, data.current_password, data.new_password
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )
    
    return ResponseMessage(message="Password changed successfully")


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get user by ID
    
    Returns public user profile.
    """
    service = UserService(db)
    user = await service.get_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    return user


@router.get("", response_model=UserListResponse)
async def get_users_list(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    group_id: Optional[int] = None,
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get users list (Admin only)
    
    Returns paginated list of all users.
    """
    service = UserService(db)
    users, total = await service.get_list(
        page=page,
        per_page=per_page,
        search=search,
        group_id=group_id,
    )
    
    pages = (total + per_page - 1) // per_page
    
    return UserListResponse(
        items=users,
        total=total,
        page=page,
        per_page=per_page,
        pages=pages,
    )


@router.post("/{user_id}/ban", response_model=ResponseMessage)
async def ban_user(
    user_id: int,
    reason: str = "Violation of terms",
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Ban user (Admin only)
    """
    service = UserService(db)
    user = await service.get_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    if user.group and user.group.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot ban an administrator",
        )
    
    await service.ban_user(user, reason)
    return ResponseMessage(message=f"User {user.username} has been banned")


@router.post("/{user_id}/unban", response_model=ResponseMessage)
async def unban_user(
    user_id: int,
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Unban user (Admin only)
    """
    service = UserService(db)
    user = await service.get_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    await service.unban_user(user)
    return ResponseMessage(message=f"User {user.username} has been unbanned")


@router.delete("/{user_id}", response_model=ResponseMessage)
async def delete_user(
    user_id: int,
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete user (Admin only)
    """
    service = UserService(db)
    user = await service.get_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    if user.group and user.group.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete an administrator",
        )
    
    await service.delete(user)
    return ResponseMessage(message="User deleted successfully")


# ============== User Groups ==============

@router.get("/groups/all", response_model=list[UserGroupResponse])
async def get_all_groups(
    db: AsyncSession = Depends(get_db),
):
    """
    Get all user groups
    """
    service = UserGroupService(db)
    groups = await service.get_all()
    return groups
