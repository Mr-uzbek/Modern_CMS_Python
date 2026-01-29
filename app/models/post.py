"""
Post (Article/News) model - The main content model
"""
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Boolean, Integer, DateTime, Text, ForeignKey, Table, Column, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User, Favorite
    from app.models.category import Category
    from app.models.comment import Comment


# Post-Category many-to-many relationship
post_categories = Table(
    "post_categories",
    Base.metadata,
    Column("post_id", Integer, ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True),
    Column("category_id", Integer, ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True),
)


# Post-Tag many-to-many relationship
post_tags = Table(
    "post_tags",
    Base.metadata,
    Column("post_id", Integer, ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)


class Tag(Base):
    """Tag model for post tagging"""
    __tablename__ = "tags"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    slug: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    posts_count: Mapped[int] = mapped_column(Integer, default=0)
    
    posts: Mapped[List["Post"]] = relationship(
        secondary=post_tags, back_populates="tags"
    )


class Post(Base):
    """Post/Article/News model"""
    __tablename__ = "posts"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    
    # Content
    title: Mapped[str] = mapped_column(String(255), index=True)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    short_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    full_content: Mapped[str] = mapped_column(Text)
    
    # Media
    thumbnail: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    images: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array
    video_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Author
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    author: Mapped["User"] = relationship(back_populates="posts")
    
    # Status
    is_published: Mapped[bool] = mapped_column(Boolean, default=False)
    is_approved: Mapped[bool] = mapped_column(Boolean, default=True)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False)
    is_pinned: Mapped[bool] = mapped_column(Boolean, default=False)
    allow_comments: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Scheduling
    publish_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # SEO
    meta_title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    meta_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    meta_keywords: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Stats
    views_count: Mapped[int] = mapped_column(Integer, default=0)
    comments_count: Mapped[int] = mapped_column(Integer, default=0)
    favorites_count: Mapped[int] = mapped_column(Integer, default=0)
    shares_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Rating
    rating: Mapped[float] = mapped_column(Float, default=0.0)
    votes_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Custom fields (JSON)
    extra_fields: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Source
    source_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    source_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    
    # Relationships
    categories: Mapped[List["Category"]] = relationship(
        secondary=post_categories, back_populates="posts"
    )
    tags: Mapped[List["Tag"]] = relationship(
        secondary=post_tags, back_populates="posts"
    )
    comments: Mapped[List["Comment"]] = relationship(back_populates="post")
    favorited_by: Mapped[List["Favorite"]] = relationship(back_populates="post")


class PostView(Base):
    """Track post views for analytics"""
    __tablename__ = "post_views"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    ip_address: Mapped[str] = mapped_column(String(45))
    user_agent: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    referer: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    viewed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class PostRating(Base):
    """Post ratings/votes"""
    __tablename__ = "post_ratings"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    ip_address: Mapped[str] = mapped_column(String(45))
    rating: Mapped[int] = mapped_column(Integer)  # 1-5 or -1/+1
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
