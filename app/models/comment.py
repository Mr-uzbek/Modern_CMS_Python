"""
Comment model for posts
"""
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Boolean, Integer, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.post import Post


class Comment(Base):
    """Comment model for posts"""
    __tablename__ = "comments"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Content
    content: Mapped[str] = mapped_column(Text)
    
    # Relations
    post_id: Mapped[int] = mapped_column(
        ForeignKey("posts.id", ondelete="CASCADE"), index=True
    )
    post: Mapped["Post"] = relationship(back_populates="comments")
    
    author_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    author: Mapped[Optional["User"]] = relationship(back_populates="comments")
    
    # For anonymous comments
    guest_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    guest_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Thread support (nested comments)
    parent_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("comments.id", ondelete="CASCADE"), nullable=True
    )
    parent: Mapped[Optional["Comment"]] = relationship(
        back_populates="replies", remote_side="Comment.id"
    )
    replies: Mapped[List["Comment"]] = relationship(back_populates="parent")
    
    # Status
    is_approved: Mapped[bool] = mapped_column(Boolean, default=True)
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Stats
    likes_count: Mapped[int] = mapped_column(Integer, default=0)
    dislikes_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Metadata
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class CommentVote(Base):
    """Comment likes/dislikes"""
    __tablename__ = "comment_votes"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    comment_id: Mapped[int] = mapped_column(
        ForeignKey("comments.id", ondelete="CASCADE"), index=True
    )
    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    ip_address: Mapped[str] = mapped_column(String(45))
    vote: Mapped[int] = mapped_column(Integer)  # 1 = like, -1 = dislike
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
