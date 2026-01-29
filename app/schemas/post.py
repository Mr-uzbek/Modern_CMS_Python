"""
Post and Category schemas
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


# ============== Tag Schemas ==============

class TagBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)


class TagCreate(TagBase):
    pass


class TagResponse(TagBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    slug: str
    posts_count: int = 0


# ============== Category Schemas ==============

class CategoryBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    icon: Optional[str] = None
    image: Optional[str] = None
    color: Optional[str] = None
    is_active: bool = True
    show_in_menu: bool = True
    position: int = 0


class CategoryCreate(CategoryBase):
    parent_id: Optional[int] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    meta_keywords: Optional[str] = None


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None
    parent_id: Optional[int] = None
    icon: Optional[str] = None
    image: Optional[str] = None
    color: Optional[str] = None
    is_active: Optional[bool] = None
    show_in_menu: Optional[bool] = None
    position: Optional[int] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    meta_keywords: Optional[str] = None


class CategoryResponse(CategoryBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    slug: str
    parent_id: Optional[int] = None
    posts_count: int = 0
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    created_at: datetime


class CategoryWithChildren(CategoryResponse):
    children: List["CategoryResponse"] = []


# ============== Post Schemas ==============

class PostAuthor(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    username: str
    full_name: Optional[str] = None
    avatar: Optional[str] = None


class PostBase(BaseModel):
    title: str = Field(..., min_length=5, max_length=255)
    short_content: Optional[str] = None
    full_content: str = Field(..., min_length=10)


class PostCreate(PostBase):
    category_ids: List[int] = []
    tags: List[str] = []
    thumbnail: Optional[str] = None
    video_url: Optional[str] = None
    is_published: bool = True
    is_featured: bool = False
    is_pinned: bool = False
    allow_comments: bool = True
    publish_date: Optional[datetime] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    meta_keywords: Optional[str] = None
    source_name: Optional[str] = None
    source_url: Optional[str] = None
    extra_fields: Optional[dict] = None


class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=255)
    short_content: Optional[str] = None
    full_content: Optional[str] = Field(None, min_length=10)
    category_ids: Optional[List[int]] = None
    tags: Optional[List[str]] = None
    thumbnail: Optional[str] = None
    video_url: Optional[str] = None
    is_published: Optional[bool] = None
    is_featured: Optional[bool] = None
    is_pinned: Optional[bool] = None
    allow_comments: Optional[bool] = None
    publish_date: Optional[datetime] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    meta_keywords: Optional[str] = None


class PostResponse(PostBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    slug: str
    thumbnail: Optional[str] = None
    video_url: Optional[str] = None
    author: PostAuthor
    categories: List[CategoryResponse] = []
    tags: List[TagResponse] = []
    is_published: bool
    is_featured: bool
    is_pinned: bool
    allow_comments: bool
    views_count: int = 0
    comments_count: int = 0
    favorites_count: int = 0
    rating: float = 0.0
    votes_count: int = 0
    created_at: datetime
    updated_at: datetime


class PostDetailResponse(PostResponse):
    """Full post details including SEO fields"""
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    meta_keywords: Optional[str] = None
    source_name: Optional[str] = None
    source_url: Optional[str] = None
    publish_date: Optional[datetime] = None


class PostListResponse(BaseModel):
    items: List[PostResponse]
    total: int
    page: int
    per_page: int
    pages: int


# ============== Post Rating ==============

class PostRatingRequest(BaseModel):
    rating: int = Field(..., ge=1, le=5)


class PostRatingResponse(BaseModel):
    rating: float
    votes_count: int
    user_rating: Optional[int] = None
