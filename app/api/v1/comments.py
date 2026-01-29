"""
Comments API endpoints
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.schemas.comment import (
    CommentCreate, CommentUpdate, CommentResponse, CommentListResponse,
    CommentVoteRequest, CommentVoteResponse
)
from app.schemas.common import ResponseMessage
from app.api.deps import get_current_user, get_current_user_optional, get_admin_user
from app.services.comment import CommentService
from app.services.post import PostService


router = APIRouter(prefix="/comments", tags=["Comments"])


def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


@router.get("/post/{post_id}", response_model=CommentListResponse)
async def get_comments_for_post(
    post_id: int,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """
    Get comments for a post
    
    Returns paginated list of approved comments.
    """
    post_service = PostService(db)
    post = await post_service.get_by_id(post_id)
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )
    
    if not post.allow_comments:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comments are disabled for this post",
        )
    
    service = CommentService(db)
    comments, total = await service.get_by_post(
        post_id=post_id,
        page=page,
        per_page=per_page,
        approved_only=True,
    )
    
    pages = (total + per_page - 1) // per_page
    
    return CommentListResponse(
        items=comments,
        total=total,
        page=page,
        per_page=per_page,
        pages=pages,
    )


@router.get("/latest", response_model=list[CommentResponse])
async def get_latest_comments(
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """
    Get latest comments
    """
    service = CommentService(db)
    comments = await service.get_latest(limit=limit)
    return comments


@router.get("/{comment_id}", response_model=CommentResponse)
async def get_comment(
    comment_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get comment by ID
    """
    service = CommentService(db)
    comment = await service.get_by_id(comment_id)
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )
    
    return comment


@router.post("", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    data: CommentCreate,
    request: Request,
    user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    """
    Create new comment
    
    Authenticated users can comment. Guest comments require name and email.
    """
    # Check post exists and allows comments
    post_service = PostService(db)
    post = await post_service.get_by_id(data.post_id)
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )
    
    if not post.allow_comments:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comments are disabled for this post",
        )
    
    # Validate guest comment
    if not user and (not data.guest_name or not data.guest_email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Guest comments require name and email",
        )
    
    # Check parent comment exists
    if data.parent_id:
        service = CommentService(db)
        parent = await service.get_by_id(data.parent_id)
        if not parent or parent.post_id != data.post_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid parent comment",
            )
    
    service = CommentService(db)
    comment = await service.create(
        data=data,
        author_id=user.id if user else None,
        ip=get_client_ip(request),
        user_agent=request.headers.get("User-Agent", ""),
    )
    
    # Update post comments count
    post.comments_count += 1
    
    return comment


@router.patch("/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: int,
    data: CommentUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update comment
    
    Users can edit their own comments. Admins can edit any comment.
    """
    service = CommentService(db)
    comment = await service.get_by_id(comment_id)
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )
    
    # Check permission
    if comment.author_id != user.id and not user.group.can_edit_comments:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to edit this comment",
        )
    
    updated = await service.update(comment, data)
    return updated


@router.delete("/{comment_id}", response_model=ResponseMessage)
async def delete_comment(
    comment_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete comment
    
    Users can delete their own comments. Admins can delete any comment.
    """
    service = CommentService(db)
    comment = await service.get_by_id(comment_id)
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )
    
    # Check permission
    if comment.author_id != user.id and not user.group.can_delete_comments:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to delete this comment",
        )
    
    # Update post comments count
    post_service = PostService(db)
    post = await post_service.get_by_id(comment.post_id)
    if post and post.comments_count > 0:
        post.comments_count -= 1
    
    await service.delete(comment)
    return ResponseMessage(message="Comment deleted successfully")


@router.post("/{comment_id}/vote", response_model=CommentVoteResponse)
async def vote_comment(
    comment_id: int,
    data: CommentVoteRequest,
    request: Request,
    user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    """
    Vote on a comment
    
    Vote values: 1 = like, -1 = dislike, 0 = remove vote
    """
    service = CommentService(db)
    comment = await service.get_by_id(comment_id)
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )
    
    likes, dislikes = await service.vote(
        comment=comment,
        vote=data.vote,
        user_id=user.id if user else None,
        ip=get_client_ip(request),
    )
    
    return CommentVoteResponse(
        likes_count=likes,
        dislikes_count=dislikes,
        user_vote=data.vote if data.vote != 0 else None,
    )


@router.post("/{comment_id}/approve", response_model=ResponseMessage)
async def approve_comment(
    comment_id: int,
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Approve comment (Admin only)
    """
    service = CommentService(db)
    comment = await service.get_by_id(comment_id)
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )
    
    await service.approve(comment)
    return ResponseMessage(message="Comment approved")


@router.post("/{comment_id}/pin", response_model=ResponseMessage)
async def pin_comment(
    comment_id: int,
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Pin comment (Admin only)
    """
    service = CommentService(db)
    comment = await service.get_by_id(comment_id)
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )
    
    await service.pin(comment)
    return ResponseMessage(message="Comment pinned")


@router.delete("/{comment_id}/pin", response_model=ResponseMessage)
async def unpin_comment(
    comment_id: int,
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Unpin comment (Admin only)
    """
    service = CommentService(db)
    comment = await service.get_by_id(comment_id)
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )
    
    await service.unpin(comment)
    return ResponseMessage(message="Comment unpinned")
