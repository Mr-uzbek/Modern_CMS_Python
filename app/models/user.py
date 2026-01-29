"""
User model and related tables
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Boolean, Integer, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class UserGroup(Base):
    """User group/role model"""
    __tablename__ = "user_groups"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    
    # Permissions
    can_add_posts: Mapped[bool] = mapped_column(Boolean, default=False)
    can_edit_posts: Mapped[bool] = mapped_column(Boolean, default=False)
    can_delete_posts: Mapped[bool] = mapped_column(Boolean, default=False)
    can_add_comments: Mapped[bool] = mapped_column(Boolean, default=True)
    can_edit_comments: Mapped[bool] = mapped_column(Boolean, default=False)
    can_delete_comments: Mapped[bool] = mapped_column(Boolean, default=False)
    can_upload_files: Mapped[bool] = mapped_column(Boolean, default=False)
    can_access_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Settings
    max_file_size: Mapped[int] = mapped_column(Integer, default=5242880)  # 5MB
    max_posts_per_day: Mapped[int] = mapped_column(Integer, default=10)
    
    # Relationships
    users: Mapped[List["User"]] = relationship(back_populates="group")
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class User(Base):
    """User account model"""
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    
    # Profile
    full_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    avatar: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    bio: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Social
    telegram: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    twitter: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    facebook: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)
    ban_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Group
    group_id: Mapped[int] = mapped_column(ForeignKey("user_groups.id"), default=1)
    group: Mapped["UserGroup"] = relationship(back_populates="users")
    
    # Stats
    posts_count: Mapped[int] = mapped_column(Integer, default=0)
    comments_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Security
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_ip: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    two_factor_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    two_factor_secret: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    
    # Relationships
    posts: Mapped[List["Post"]] = relationship(back_populates="author")
    comments: Mapped[List["Comment"]] = relationship(back_populates="author")
    favorites: Mapped[List["Favorite"]] = relationship(back_populates="user")


class Favorite(Base):
    """User favorites/bookmarks"""
    __tablename__ = "favorites"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    user: Mapped["User"] = relationship(back_populates="favorites")
    post: Mapped["Post"] = relationship(back_populates="favorited_by")


# Import Post and Comment to avoid circular imports
from app.models.post import Post
from app.models.comment import Comment
