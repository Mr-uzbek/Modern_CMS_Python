"""
Schemas package - Export all schemas
"""
from app.schemas.user import (
    UserGroupCreate, UserGroupUpdate, UserGroupResponse,
    UserCreate, UserUpdate, UserResponse, UserProfileResponse,
    UserAdminResponse, UserListResponse, UserPasswordChange,
    LoginRequest, TokenResponse, RefreshTokenRequest,
    RegisterRequest, PasswordResetRequest, PasswordResetConfirm
)
from app.schemas.post import (
    TagCreate, TagResponse,
    CategoryCreate, CategoryUpdate, CategoryResponse, CategoryWithChildren,
    PostCreate, PostUpdate, PostResponse, PostDetailResponse, PostListResponse,
    PostRatingRequest, PostRatingResponse
)
from app.schemas.comment import (
    CommentCreate, CommentUpdate, CommentResponse, CommentListResponse,
    CommentVoteRequest, CommentVoteResponse
)
from app.schemas.cms import (
    StaticPageCreate, StaticPageUpdate, StaticPageResponse,
    BannerCreate, BannerUpdate, BannerResponse,
    SettingCreate, SettingUpdate, SettingResponse, SettingsBulkUpdate,
    MenuItemCreate, MenuItemUpdate, MenuItemResponse,
    RedirectCreate, RedirectUpdate, RedirectResponse
)
from app.schemas.common import (
    ResponseMessage, ErrorResponse, PaginatedResponse,
    HealthCheckResponse, StatsResponse, SearchRequest,
    UploadResponse, BulkActionRequest, BulkActionResponse
)


__all__ = [
    # User
    "UserGroupCreate", "UserGroupUpdate", "UserGroupResponse",
    "UserCreate", "UserUpdate", "UserResponse", "UserProfileResponse",
    "UserAdminResponse", "UserListResponse", "UserPasswordChange",
    "LoginRequest", "TokenResponse", "RefreshTokenRequest",
    "RegisterRequest", "PasswordResetRequest", "PasswordResetConfirm",
    # Post
    "TagCreate", "TagResponse",
    "CategoryCreate", "CategoryUpdate", "CategoryResponse", "CategoryWithChildren",
    "PostCreate", "PostUpdate", "PostResponse", "PostDetailResponse", "PostListResponse",
    "PostRatingRequest", "PostRatingResponse",
    # Comment
    "CommentCreate", "CommentUpdate", "CommentResponse", "CommentListResponse",
    "CommentVoteRequest", "CommentVoteResponse",
    # CMS
    "StaticPageCreate", "StaticPageUpdate", "StaticPageResponse",
    "BannerCreate", "BannerUpdate", "BannerResponse",
    "SettingCreate", "SettingUpdate", "SettingResponse", "SettingsBulkUpdate",
    "MenuItemCreate", "MenuItemUpdate", "MenuItemResponse",
    "RedirectCreate", "RedirectUpdate", "RedirectResponse",
    # Common
    "ResponseMessage", "ErrorResponse", "PaginatedResponse",
    "HealthCheckResponse", "StatsResponse", "SearchRequest",
    "UploadResponse", "BulkActionRequest", "BulkActionResponse",
]
