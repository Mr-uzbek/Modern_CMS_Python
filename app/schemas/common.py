"""
Common schemas for API responses
"""
from typing import Optional, Any, TypeVar, Generic, List
from pydantic import BaseModel


T = TypeVar("T")


class ResponseMessage(BaseModel):
    """Simple message response"""
    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated list response"""
    items: List[T]
    total: int
    page: int
    per_page: int
    pages: int


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    database: str
    cache: str


class StatsResponse(BaseModel):
    """Dashboard statistics"""
    total_posts: int
    total_users: int
    total_comments: int
    total_categories: int
    total_tags: int
    posts_today: int
    comments_today: int
    users_today: int


class SearchRequest(BaseModel):
    """Search query parameters"""
    query: str
    category_id: Optional[int] = None
    tags: Optional[List[str]] = None
    author_id: Optional[int] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    sort_by: str = "created_at"
    sort_order: str = "desc"


class UploadResponse(BaseModel):
    """File upload response"""
    filename: str
    url: str
    size: int
    mime_type: str


class BulkActionRequest(BaseModel):
    """Bulk action request"""
    ids: List[int]
    action: str  # delete, publish, unpublish, etc.


class BulkActionResponse(BaseModel):
    """Bulk action response"""
    success: bool
    affected: int
    errors: List[str] = []
