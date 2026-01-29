"""
Comment schemas
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, ConfigDict


class CommentAuthor(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    username: str
    full_name: Optional[str] = None
    avatar: Optional[str] = None


class CommentBase(BaseModel):
    content: str = Field(..., min_length=3, max_length=5000)


class CommentCreate(CommentBase):
    post_id: int
    parent_id: Optional[int] = None
    # For guest comments
    guest_name: Optional[str] = Field(None, min_length=2, max_length=100)
    guest_email: Optional[EmailStr] = None


class CommentUpdate(BaseModel):
    content: str = Field(..., min_length=3, max_length=5000)


class CommentResponse(CommentBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    post_id: int
    author: Optional[CommentAuthor] = None
    guest_name: Optional[str] = None
    parent_id: Optional[int] = None
    is_approved: bool
    is_pinned: bool
    likes_count: int = 0
    dislikes_count: int = 0
    created_at: datetime
    updated_at: datetime
    replies: List["CommentResponse"] = []


class CommentListResponse(BaseModel):
    items: List[CommentResponse]
    total: int
    page: int
    per_page: int
    pages: int


class CommentVoteRequest(BaseModel):
    vote: int = Field(..., ge=-1, le=1)  # -1 = dislike, 0 = remove, 1 = like


class CommentVoteResponse(BaseModel):
    likes_count: int
    dislikes_count: int
    user_vote: Optional[int] = None
