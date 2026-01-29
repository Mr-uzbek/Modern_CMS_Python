"""
Categories and Tags API endpoints
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.schemas.post import (
    CategoryCreate, CategoryUpdate, CategoryResponse, CategoryWithChildren,
    TagResponse
)
from app.schemas.common import ResponseMessage
from app.api.deps import get_admin_user
from app.services.category import CategoryService, TagService


router = APIRouter(tags=["Categories & Tags"])


# ============== Categories ==============

@router.get("/categories", response_model=list[CategoryResponse])
async def get_categories(
    active_only: bool = True,
    db: AsyncSession = Depends(get_db),
):
    """
    Get all categories
    """
    service = CategoryService(db)
    categories = await service.get_all(active_only=active_only)
    return categories


@router.get("/categories/tree", response_model=list[CategoryWithChildren])
async def get_categories_tree(
    db: AsyncSession = Depends(get_db),
):
    """
    Get categories as tree structure
    """
    service = CategoryService(db)
    categories = await service.get_tree()
    return categories


@router.get("/categories/menu", response_model=list[CategoryWithChildren])
async def get_menu_categories(
    db: AsyncSession = Depends(get_db),
):
    """
    Get categories for menu display
    """
    service = CategoryService(db)
    categories = await service.get_menu_categories()
    return categories


@router.get("/categories/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int,
    db: AsyncSession = Depends(get_db),
):
    """
    Get category by ID
    """
    service = CategoryService(db)
    category = await service.get_by_id(category_id)
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )
    
    return category


@router.get("/categories/slug/{slug}", response_model=CategoryResponse)
async def get_category_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get category by slug
    """
    service = CategoryService(db)
    category = await service.get_by_slug(slug)
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )
    
    return category


@router.post("/categories", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    data: CategoryCreate,
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create new category (Admin only)
    """
    service = CategoryService(db)
    
    # Check parent exists
    if data.parent_id:
        parent = await service.get_by_id(data.parent_id)
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Parent category not found",
            )
    
    category = await service.create(data)
    return category


@router.patch("/categories/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    data: CategoryUpdate,
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update category (Admin only)
    """
    service = CategoryService(db)
    category = await service.get_by_id(category_id)
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )
    
    # Prevent circular reference
    if data.parent_id and data.parent_id == category_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category cannot be its own parent",
        )
    
    updated = await service.update(category, data)
    return updated


@router.delete("/categories/{category_id}", response_model=ResponseMessage)
async def delete_category(
    category_id: int,
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete category (Admin only)
    """
    service = CategoryService(db)
    category = await service.get_by_id(category_id)
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found",
        )
    
    if category.posts_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete category with {category.posts_count} posts",
        )
    
    await service.delete(category)
    return ResponseMessage(message="Category deleted successfully")


# ============== Tags ==============

@router.get("/tags", response_model=list[TagResponse])
async def get_tags(
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    """
    Get all tags
    """
    service = TagService(db)
    tags = await service.get_all(limit=limit)
    return tags


@router.get("/tags/popular", response_model=list[TagResponse])
async def get_popular_tags(
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    """
    Get popular tags
    """
    service = TagService(db)
    tags = await service.get_popular(limit=limit)
    return tags


@router.get("/tags/search", response_model=list[TagResponse])
async def search_tags(
    q: str = Query(..., min_length=1),
    limit: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """
    Search tags by name
    """
    service = TagService(db)
    tags = await service.search(q, limit=limit)
    return tags


@router.get("/tags/{slug}", response_model=TagResponse)
async def get_tag_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Get tag by slug
    """
    service = TagService(db)
    tag = await service.get_by_slug(slug)
    
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found",
        )
    
    return tag


@router.delete("/tags/{tag_id}", response_model=ResponseMessage)
async def delete_tag(
    tag_id: int,
    admin: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete tag (Admin only)
    """
    service = TagService(db)
    tag = await service.get_by_id(tag_id)
    
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found",
        )
    
    await service.delete(tag)
    return ResponseMessage(message="Tag deleted successfully")
