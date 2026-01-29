"""
User schemas for API request/response validation
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field, ConfigDict


# ============== User Group Schemas ==============

class UserGroupBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    can_add_posts: bool = False
    can_edit_posts: bool = False
    can_delete_posts: bool = False
    can_add_comments: bool = True
    can_edit_comments: bool = False
    can_delete_comments: bool = False
    can_upload_files: bool = False
    can_access_admin: bool = False
    is_admin: bool = False
    max_file_size: int = 5242880
    max_posts_per_day: int = 10


class UserGroupCreate(UserGroupBase):
    pass


class UserGroupUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    can_add_posts: Optional[bool] = None
    can_edit_posts: Optional[bool] = None
    can_delete_posts: Optional[bool] = None
    can_add_comments: Optional[bool] = None
    can_edit_comments: Optional[bool] = None
    can_delete_comments: Optional[bool] = None
    can_upload_files: Optional[bool] = None
    can_access_admin: Optional[bool] = None
    is_admin: Optional[bool] = None


class UserGroupResponse(UserGroupBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime


# ============== User Schemas ==============

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)
    full_name: Optional[str] = None


class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, max_length=100)
    avatar: Optional[str] = Field(None, max_length=255)
    bio: Optional[str] = Field(None, max_length=500)
    website: Optional[str] = Field(None, max_length=255)
    telegram: Optional[str] = None
    twitter: Optional[str] = None
    facebook: Optional[str] = None


class UserPasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)


class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    full_name: Optional[str] = None
    avatar: Optional[str] = None
    bio: Optional[str] = None
    website: Optional[str] = None
    telegram: Optional[str] = None
    twitter: Optional[str] = None
    facebook: Optional[str] = None
    is_active: bool
    is_verified: bool
    posts_count: int = 0
    comments_count: int = 0
    created_at: datetime


class UserProfileResponse(UserResponse):
    group: UserGroupResponse


class UserAdminResponse(UserProfileResponse):
    """Extended response for admin panel"""
    is_banned: bool
    ban_reason: Optional[str] = None
    last_login: Optional[datetime] = None
    last_ip: Optional[str] = None
    two_factor_enabled: bool


class UserListResponse(BaseModel):
    items: List[UserResponse]
    total: int
    page: int
    per_page: int
    pages: int


# ============== Auth Schemas ==============

class LoginRequest(BaseModel):
    username: str
    password: str
    remember_me: bool = False


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class RegisterRequest(UserCreate):
    pass


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=100)
