"""
Comment service
"""
from typing import Optional, List
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.comment import Comment, CommentVote
from app.schemas.comment import CommentCreate, CommentUpdate


class CommentService:
    """Service for comment operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, comment_id: int) -> Optional[Comment]:
        """Get comment by ID"""
        result = await self.db.execute(
            select(Comment)
            .options(selectinload(Comment.author), selectinload(Comment.replies))
            .where(Comment.id == comment_id)
        )
        return result.scalar_one_or_none()
    
    async def create(
        self,
        data: CommentCreate,
        author_id: Optional[int] = None,
        ip: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Comment:
        """Create new comment"""
        comment = Comment(
            content=data.content,
            post_id=data.post_id,
            parent_id=data.parent_id,
            author_id=author_id,
            guest_name=data.guest_name if not author_id else None,
            guest_email=data.guest_email if not author_id else None,
            ip_address=ip,
            user_agent=user_agent[:255] if user_agent else None,
        )
        
        self.db.add(comment)
        await self.db.flush()
        await self.db.refresh(comment)
        return comment
    
    async def update(self, comment: Comment, data: CommentUpdate) -> Comment:
        """Update comment"""
        comment.content = data.content
        await self.db.flush()
        await self.db.refresh(comment)
        return comment
    
    async def delete(self, comment: Comment) -> None:
        """Delete comment and all replies"""
        await self.db.delete(comment)
        await self.db.flush()
    
    async def approve(self, comment: Comment) -> None:
        """Approve comment"""
        comment.is_approved = True
        await self.db.flush()
    
    async def pin(self, comment: Comment) -> None:
        """Pin comment"""
        comment.is_pinned = True
        await self.db.flush()
    
    async def unpin(self, comment: Comment) -> None:
        """Unpin comment"""
        comment.is_pinned = False
        await self.db.flush()
    
    async def get_by_post(
        self,
        post_id: int,
        page: int = 1,
        per_page: int = 20,
        approved_only: bool = True,
    ) -> tuple[List[Comment], int]:
        """Get comments for a post"""
        query = (
            select(Comment)
            .options(selectinload(Comment.author), selectinload(Comment.replies).selectinload(Comment.author))
            .where(Comment.post_id == post_id, Comment.parent_id == None)
        )
        count_query = select(func.count(Comment.id)).where(
            Comment.post_id == post_id, Comment.parent_id == None
        )
        
        if approved_only:
            query = query.where(Comment.is_approved == True)
            count_query = count_query.where(Comment.is_approved == True)
        
        # Get total count
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Sort: pinned first, then by date
        query = query.order_by(Comment.is_pinned.desc(), Comment.created_at.desc())
        
        # Apply pagination
        offset = (page - 1) * per_page
        query = query.offset(offset).limit(per_page)
        
        result = await self.db.execute(query)
        comments = list(result.scalars().unique().all())
        
        return comments, total
    
    async def get_latest(self, limit: int = 10) -> List[Comment]:
        """Get latest comments"""
        result = await self.db.execute(
            select(Comment)
            .options(selectinload(Comment.author))
            .where(Comment.is_approved == True)
            .order_by(Comment.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_by_user(
        self,
        user_id: int,
        page: int = 1,
        per_page: int = 20,
    ) -> tuple[List[Comment], int]:
        """Get comments by user"""
        query = (
            select(Comment)
            .options(selectinload(Comment.author))
            .where(Comment.author_id == user_id)
        )
        count_query = select(func.count(Comment.id)).where(Comment.author_id == user_id)
        
        # Get total count
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Apply pagination
        offset = (page - 1) * per_page
        query = query.order_by(Comment.created_at.desc()).offset(offset).limit(per_page)
        
        result = await self.db.execute(query)
        comments = list(result.scalars().all())
        
        return comments, total
    
    async def vote(
        self,
        comment: Comment,
        vote: int,
        user_id: Optional[int],
        ip: str,
    ) -> tuple[int, int]:
        """Vote on a comment (like/dislike)"""
        # Check existing vote
        existing = await self.db.execute(
            select(CommentVote).where(
                CommentVote.comment_id == comment.id,
                or_(
                    CommentVote.user_id == user_id if user_id else False,
                    CommentVote.ip_address == ip,
                )
            )
        )
        existing_vote = existing.scalar_one_or_none()
        
        if existing_vote:
            old_vote = existing_vote.vote
            
            if vote == 0:
                # Remove vote
                await self.db.delete(existing_vote)
                if old_vote == 1:
                    comment.likes_count -= 1
                else:
                    comment.dislikes_count -= 1
            else:
                # Update vote
                existing_vote.vote = vote
                if old_vote != vote:
                    if vote == 1:
                        comment.likes_count += 1
                        comment.dislikes_count -= 1
                    else:
                        comment.likes_count -= 1
                        comment.dislikes_count += 1
        else:
            if vote != 0:
                # Add new vote
                new_vote = CommentVote(
                    comment_id=comment.id,
                    user_id=user_id,
                    ip_address=ip,
                    vote=vote,
                )
                self.db.add(new_vote)
                
                if vote == 1:
                    comment.likes_count += 1
                else:
                    comment.dislikes_count += 1
        
        await self.db.flush()
        return comment.likes_count, comment.dislikes_count
    
    async def get_pending_count(self) -> int:
        """Get count of pending (unapproved) comments"""
        result = await self.db.execute(
            select(func.count(Comment.id)).where(Comment.is_approved == False)
        )
        return result.scalar() or 0
