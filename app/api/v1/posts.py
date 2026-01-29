"""
Posts API endpoints
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.config import settings
from app.models.user import User
from app.schemas.post import (
    PostCreate, PostUpdate, PostResponse, PostDetailResponse, PostListResponse,
    PostRatingRequest, PostRatingResponse
)
from app.schemas.common import ResponseMessage
from app.api.deps import get_current_user, get_current_user_optional, require_permission
from app.services.post import PostService
from app.services.user import UserService


router = APIRouter(prefix="/posts", tags=["Posts"])


def get_client_ip(request: Request) -> str:
    """Get client IP from request"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


@router.get("", response_model=PostListResponse)
async def get_posts(
    page: int = Query(1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    category_id: Optional[int] = None,
    tag: Optional[str] = None,
    author_id: Optional[int] = None,
    search: Optional[str] = None,
    is_featured: Optional[bool] = None,
    sort_by: str = Query("created_at", pattern="^(created_at|views_count|rating|comments_count)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$"),
    db: AsyncSession = Depends(get_db),
):
    """
    Get list of posts
    
    Returns paginated list of published posts with optional filtering.
    """
    service = PostService(db)
    posts, total = await service.get_list(
        page=page,
        per_page=per_page,
        category_id=category_id,
        tag=tag,
        author_id=author_id,
        search=search,
        is_published=True,
        is_featured=is_featured,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    
    pages = (total + per_page - 1) // per_page
    
    return PostListResponse(
        items=posts,
        total=total,
        page=page,
        per_page=per_page,
        pages=pages,
    )


@router.get("/featured", response_model=list[PostResponse])
async def get_featured_posts(
    limit: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
):
    """
    Get featured posts
    """
    service = PostService(db)
    posts = await service.get_featured(limit)
    return posts


@router.get("/popular", response_model=list[PostResponse])
async def get_popular_posts(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """
    Get popular posts by views
    """
    service = PostService(db)
    posts = await service.get_popular(limit)
    return posts


@router.get("/recent", response_model=list[PostResponse])
async def get_recent_posts(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """
    Get recent posts
    """
    service = PostService(db)
    posts = await service.get_recent(limit)
    return posts


@router.get("/{post_id}", response_model=PostDetailResponse)
async def get_post(
    post_id: int,
    request: Request,
    user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    """
    Get post by ID
    
    Returns full post details and increments view count.
    """
    service = PostService(db)
    post = await service.get_by_id(post_id)
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )
    
    if not post.is_published:
        # Only author or admin can see unpublished posts
        if not user or (user.id != post.author_id and not user.group.can_access_admin):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found",
            )
    
    # Track view
    await service.increment_views(
        post,
        user_id=user.id if user else None,
        ip=get_client_ip(request),
        user_agent=request.headers.get("User-Agent", ""),
        referer=request.headers.get("Referer"),
    )
    
    return post


@router.get("/slug/{slug}", response_model=PostDetailResponse)
async def get_post_by_slug(
    slug: str,
    request: Request,
    user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    """
    Get post by slug
    """
    service = PostService(db)
    post = await service.get_by_slug(slug)
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )
    
    if not post.is_published:
        if not user or (user.id != post.author_id and not user.group.can_access_admin):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Post not found",
            )
    
    # Track view
    await service.increment_views(
        post,
        user_id=user.id if user else None,
        ip=get_client_ip(request),
        user_agent=request.headers.get("User-Agent", ""),
        referer=request.headers.get("Referer"),
    )
    
    return post


@router.get("/{post_id}/related", response_model=list[PostResponse])
async def get_related_posts(
    post_id: int,
    limit: int = Query(5, ge=1, le=20),
    db: AsyncSession = Depends(get_db),
):
    """
    Get related posts
    """
    service = PostService(db)
    post = await service.get_by_id(post_id)
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )
    
    related = await service.get_related(post, limit)
    return related


@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
async def create_post(
    data: PostCreate,
    user: User = Depends(require_permission("can_add_posts")),
    db: AsyncSession = Depends(get_db),
):
    """
    Create new post
    
    Requires 'can_add_posts' permission.
    """
    service = PostService(db)
    post = await service.create(data, author_id=user.id)
    
    # Update user's posts count
    user_service = UserService(db)
    await user_service.increment_posts_count(user)
    
    return post


@router.patch("/{post_id}", response_model=PostResponse)
async def update_post(
    post_id: int,
    data: PostUpdate,
    user: User = Depends(require_permission("can_edit_posts")),
    db: AsyncSession = Depends(get_db),
):
    """
    Update post
    
    Author can edit own posts. Users with 'can_edit_posts' permission can edit any post.
    """
    service = PostService(db)
    post = await service.get_by_id(post_id)
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )
    
    # Check permission
    if post.author_id != user.id and not user.group.can_edit_posts:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to edit this post",
        )
    
    updated_post = await service.update(post, data)
    return updated_post


@router.delete("/{post_id}", response_model=ResponseMessage)
async def delete_post(
    post_id: int,
    user: User = Depends(require_permission("can_delete_posts")),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete post
    
    Requires 'can_delete_posts' permission or must be the author.
    """
    service = PostService(db)
    post = await service.get_by_id(post_id)
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )
    
    # Check permission
    if post.author_id != user.id and not user.group.can_delete_posts:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to delete this post",
        )
    
    await service.delete(post)
    return ResponseMessage(message="Post deleted successfully")


@router.post("/{post_id}/rate", response_model=PostRatingResponse)
async def rate_post(
    post_id: int,
    data: PostRatingRequest,
    request: Request,
    user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    """
    Rate a post
    
    Rating must be between 1 and 5.
    """
    service = PostService(db)
    post = await service.get_by_id(post_id)
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )
    
    rating, votes_count = await service.rate_post(
        post,
        rating=data.rating,
        user_id=user.id if user else None,
        ip=get_client_ip(request),
    )
    
    return PostRatingResponse(
        rating=rating,
        votes_count=votes_count,
        user_rating=data.rating,
    )
