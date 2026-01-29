"""
Static pages, Banners, Settings and other CMS models
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Boolean, Integer, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class StaticPage(Base):
    """Static pages (About, Contact, etc.)"""
    __tablename__ = "static_pages"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    slug: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)
    
    # Display
    template: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    show_in_menu: Mapped[bool] = mapped_column(Boolean, default=False)
    menu_position: Mapped[int] = mapped_column(Integer, default=0)
    
    # SEO
    meta_title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    meta_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    meta_keywords: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class Banner(Base):
    """Banner/Advertisement model"""
    __tablename__ = "banners"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    position: Mapped[str] = mapped_column(String(50), index=True)  # header, sidebar, footer, etc.
    
    # Content - either image or HTML
    image_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    html_code: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    link_url: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    alt_text: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Targeting
    show_on_pages: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array
    show_to_groups: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array
    
    # Scheduling
    start_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    end_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    display_order: Mapped[int] = mapped_column(Integer, default=0)
    
    # Stats
    views_count: Mapped[int] = mapped_column(Integer, default=0)
    clicks_count: Mapped[int] = mapped_column(Integer, default=0)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Setting(Base):
    """System settings key-value store"""
    __tablename__ = "settings"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    type: Mapped[str] = mapped_column(String(20), default="string")  # string, int, bool, json
    group: Mapped[str] = mapped_column(String(50), default="general")
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )


class Menu(Base):
    """Navigation menu items"""
    __tablename__ = "menus"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    location: Mapped[str] = mapped_column(String(50), index=True)  # header, footer, sidebar
    
    title: Mapped[str] = mapped_column(String(100))
    url: Mapped[str] = mapped_column(String(255))
    icon: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    target: Mapped[str] = mapped_column(String(20), default="_self")
    
    # Hierarchy
    parent_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    position: Mapped[int] = mapped_column(Integer, default=0)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Redirect(Base):
    """URL redirects"""
    __tablename__ = "redirects"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    from_url: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    to_url: Mapped[str] = mapped_column(String(255))
    status_code: Mapped[int] = mapped_column(Integer, default=301)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    hits_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
