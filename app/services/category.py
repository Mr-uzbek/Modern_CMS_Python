"""
Category and Tag services
"""
from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from slugify import slugify

from app.models.category import Category
from app.models.post import Tag
from app.schemas.post import CategoryCreate, CategoryUpdate


class CategoryService:
    """Service for category operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, category_id: int) -> Optional[Category]:
        """Get category by ID"""
        result = await self.db.execute(
            select(Category)
            .options(selectinload(Category.children))
            .where(Category.id == category_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_slug(self, slug: str) -> Optional[Category]:
        """Get category by slug"""
        result = await self.db.execute(
            select(Category)
            .options(selectinload(Category.children))
            .where(Category.slug == slug)
        )
        return result.scalar_one_or_none()
    
    async def create(self, data: CategoryCreate) -> Category:
        """Create new category"""
        slug = slugify(data.name)
        counter = 1
        base_slug = slug
        while await self.get_by_slug(slug):
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        category = Category(
            name=data.name,
            slug=slug,
            description=data.description,
            parent_id=data.parent_id,
            icon=data.icon,
            image=data.image,
            color=data.color,
            is_active=data.is_active,
            show_in_menu=data.show_in_menu,
            position=data.position,
            meta_title=data.meta_title,
            meta_description=data.meta_description,
            meta_keywords=data.meta_keywords,
        )
        
        self.db.add(category)
        await self.db.flush()
        await self.db.refresh(category)
        return category
    
    async def update(self, category: Category, data: CategoryUpdate) -> Category:
        """Update category"""
        update_data = data.model_dump(exclude_unset=True)
        
        if "name" in update_data:
            new_slug = slugify(update_data["name"])
            if new_slug != category.slug:
                counter = 1
                base_slug = new_slug
                while True:
                    existing = await self.get_by_slug(new_slug)
                    if not existing or existing.id == category.id:
                        break
                    new_slug = f"{base_slug}-{counter}"
                    counter += 1
                update_data["slug"] = new_slug
        
        for field, value in update_data.items():
            setattr(category, field, value)
        
        await self.db.flush()
        await self.db.refresh(category)
        return category
    
    async def delete(self, category: Category) -> None:
        """Delete category"""
        await self.db.delete(category)
        await self.db.flush()
    
    async def get_all(self, active_only: bool = False) -> List[Category]:
        """Get all categories"""
        query = select(Category).options(selectinload(Category.children))
        
        if active_only:
            query = query.where(Category.is_active == True)
        
        query = query.order_by(Category.position, Category.name)
        
        result = await self.db.execute(query)
        return list(result.scalars().unique().all())
    
    async def get_tree(self, active_only: bool = True) -> List[Category]:
        """Get categories as tree (only root categories with children loaded)"""
        query = (
            select(Category)
            .options(selectinload(Category.children))
            .where(Category.parent_id == None)
        )
        
        if active_only:
            query = query.where(Category.is_active == True)
        
        query = query.order_by(Category.position, Category.name)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_menu_categories(self) -> List[Category]:
        """Get categories shown in menu"""
        result = await self.db.execute(
            select(Category)
            .options(selectinload(Category.children))
            .where(Category.is_active == True, Category.show_in_menu == True, Category.parent_id == None)
            .order_by(Category.position, Category.name)
        )
        return list(result.scalars().all())
    
    async def increment_posts_count(self, category: Category) -> None:
        """Increment posts count"""
        category.posts_count += 1
        await self.db.flush()
    
    async def decrement_posts_count(self, category: Category) -> None:
        """Decrement posts count"""
        if category.posts_count > 0:
            category.posts_count -= 1
            await self.db.flush()


class TagService:
    """Service for tag operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, tag_id: int) -> Optional[Tag]:
        """Get tag by ID"""
        result = await self.db.execute(
            select(Tag).where(Tag.id == tag_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_slug(self, slug: str) -> Optional[Tag]:
        """Get tag by slug"""
        result = await self.db.execute(
            select(Tag).where(Tag.slug == slug)
        )
        return result.scalar_one_or_none()
    
    async def get_or_create(self, name: str) -> Tag:
        """Get existing tag or create new one"""
        slug = slugify(name)
        tag = await self.get_by_slug(slug)
        
        if not tag:
            tag = Tag(name=name, slug=slug)
            self.db.add(tag)
            await self.db.flush()
        
        return tag
    
    async def get_all(self, limit: int = 100) -> List[Tag]:
        """Get all tags"""
        result = await self.db.execute(
            select(Tag).order_by(Tag.posts_count.desc()).limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_popular(self, limit: int = 20) -> List[Tag]:
        """Get popular tags"""
        result = await self.db.execute(
            select(Tag)
            .where(Tag.posts_count > 0)
            .order_by(Tag.posts_count.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def search(self, query: str, limit: int = 10) -> List[Tag]:
        """Search tags by name"""
        result = await self.db.execute(
            select(Tag)
            .where(Tag.name.ilike(f"%{query}%"))
            .order_by(Tag.posts_count.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def delete(self, tag: Tag) -> None:
        """Delete tag"""
        await self.db.delete(tag)
        await self.db.flush()
