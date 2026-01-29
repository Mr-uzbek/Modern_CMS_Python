"""
CMS schemas - Static pages, Banners, Settings, etc.
"""
from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field, ConfigDict


# ============== Static Page Schemas ==============

class StaticPageBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    title: str = Field(..., min_length=2, max_length=255)
    content: str


class StaticPageCreate(StaticPageBase):
    template: Optional[str] = None
    show_in_menu: bool = False
    menu_position: int = 0
    is_active: bool = True
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    meta_keywords: Optional[str] = None


class StaticPageUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    title: Optional[str] = Field(None, min_length=2, max_length=255)
    content: Optional[str] = None
    template: Optional[str] = None
    show_in_menu: Optional[bool] = None
    menu_position: Optional[int] = None
    is_active: Optional[bool] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    meta_keywords: Optional[str] = None


class StaticPageResponse(StaticPageBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    slug: str
    template: Optional[str] = None
    show_in_menu: bool
    menu_position: int
    is_active: bool
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    created_at: datetime
    updated_at: datetime


# ============== Banner Schemas ==============

class BannerBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    position: str = Field(..., min_length=2, max_length=50)


class BannerCreate(BannerBase):
    image_url: Optional[str] = None
    html_code: Optional[str] = None
    link_url: Optional[str] = None
    alt_text: Optional[str] = None
    is_active: bool = True
    display_order: int = 0
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class BannerUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    position: Optional[str] = None
    image_url: Optional[str] = None
    html_code: Optional[str] = None
    link_url: Optional[str] = None
    alt_text: Optional[str] = None
    is_active: Optional[bool] = None
    display_order: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class BannerResponse(BannerBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    image_url: Optional[str] = None
    html_code: Optional[str] = None
    link_url: Optional[str] = None
    alt_text: Optional[str] = None
    is_active: bool
    display_order: int
    views_count: int = 0
    clicks_count: int = 0
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    created_at: datetime


# ============== Settings Schemas ==============

class SettingBase(BaseModel):
    key: str = Field(..., min_length=2, max_length=100)
    value: Optional[str] = None
    type: str = "string"
    group: str = "general"


class SettingCreate(SettingBase):
    description: Optional[str] = None


class SettingUpdate(BaseModel):
    value: Optional[str] = None
    type: Optional[str] = None
    group: Optional[str] = None
    description: Optional[str] = None


class SettingResponse(SettingBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    description: Optional[str] = None
    updated_at: datetime


class SettingsBulkUpdate(BaseModel):
    settings: dict[str, Any]


# ============== Menu Schemas ==============

class MenuItemBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    url: str = Field(..., min_length=1, max_length=255)


class MenuItemCreate(MenuItemBase):
    name: str
    location: str
    icon: Optional[str] = None
    target: str = "_self"
    parent_id: Optional[int] = None
    position: int = 0
    is_active: bool = True


class MenuItemUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    url: Optional[str] = None
    icon: Optional[str] = None
    target: Optional[str] = None
    parent_id: Optional[int] = None
    position: Optional[int] = None
    is_active: Optional[bool] = None


class MenuItemResponse(MenuItemBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    location: str
    icon: Optional[str] = None
    target: str
    parent_id: Optional[int] = None
    position: int
    is_active: bool
    children: List["MenuItemResponse"] = []


# ============== Redirect Schemas ==============

class RedirectBase(BaseModel):
    from_url: str = Field(..., min_length=1, max_length=255)
    to_url: str = Field(..., min_length=1, max_length=255)


class RedirectCreate(RedirectBase):
    status_code: int = 301
    is_active: bool = True


class RedirectUpdate(BaseModel):
    from_url: Optional[str] = None
    to_url: Optional[str] = None
    status_code: Optional[int] = None
    is_active: Optional[bool] = None


class RedirectResponse(RedirectBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    status_code: int
    is_active: bool
    hits_count: int = 0
    created_at: datetime
