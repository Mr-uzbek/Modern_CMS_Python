"""
Post service - Business logic for content management
"""
import json
from datetime import datetime
from typing import Optional, List
from sqlalchemy import select, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from slugify import slugify

from app.models.post import Post, Tag, PostView, PostRating, post_categories, post_tags
from app.models.category import Category
from app.models.user import User
from app.schemas.post import PostCreate, PostUpdate


class PostService:
    """Service for post-related operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, post_id: int) -> Optional[Post]:
        """Get post by ID with relations"""
        result = await self.db.execute(
            select(Post)
            .options(
                selectinload(Post.author).selectinload(User.group),
                selectinload(Post.categories),
                selectinload(Post.tags),
            )
            .where(Post.id == post_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_slug(self, slug: str) -> Optional[Post]:
        """Get post by slug"""
        result = await self.db.execute(
            select(Post)
            .options(
                selectinload(Post.author).selectinload(User.group),
                selectinload(Post.categories),
                selectinload(Post.tags),
            )
            .where(Post.slug == slug)
        )
        return result.scalar_one_or_none()
    
    async def create(self, data: PostCreate, author_id: int) -> Post:
        """Create new post"""
        # Generate unique slug
        base_slug = slugify(data.title)
        slug = base_slug
        counter = 1
        while await self.get_by_slug(slug):
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        # Handle extra fields
        extra_fields = None
        if data.extra_fields:
            extra_fields = json.dumps(data.extra_fields)
        
        post = Post(
            title=data.title,
            slug=slug,
            short_content=data.short_content,
            full_content=data.full_content,
            thumbnail=data.thumbnail,
            video_url=data.video_url,
            author_id=author_id,
            is_published=data.is_published,
            is_featured=data.is_featured,
            is_pinned=data.is_pinned,
            allow_comments=data.allow_comments,
            publish_date=data.publish_date,
            meta_title=data.meta_title,
            meta_description=data.meta_description,
            meta_keywords=data.meta_keywords,
            source_name=data.source_name,
            source_url=data.source_url,
            extra_fields=extra_fields,
        )
        
        self.db.add(post)
        await self.db.flush()
        
        # Add categories
        if data.category_ids:
            await self._set_categories(post, data.category_ids)
        
        # Add tags
        if data.tags:
            await self._set_tags(post, data.tags)
        
        await self.db.refresh(post)
        return post
    
    async def update(self, post: Post, data: PostUpdate) -> Post:
        """Update post"""
        update_data = data.model_dump(exclude_unset=True, exclude={"category_ids", "tags"})
        
        # Update slug if title changed
        if "title" in update_data:
            new_slug = slugify(update_data["title"])
            if new_slug != post.slug:
                counter = 1
                base_slug = new_slug
                while True:
                    existing = await self.get_by_slug(new_slug)
                    if not existing or existing.id == post.id:
                        break
                    new_slug = f"{base_slug}-{counter}"
                    counter += 1
                update_data["slug"] = new_slug
        
        for field, value in update_data.items():
            setattr(post, field, value)
        
        # Update categories
        if data.category_ids is not None:
            await self._set_categories(post, data.category_ids)
        
        # Update tags
        if data.tags is not None:
            await self._set_tags(post, data.tags)
        
        await self.db.flush()
        await self.db.refresh(post)
        return post
    
    async def delete(self, post: Post) -> None:
        """Delete post"""
        await self.db.delete(post)
        await self.db.flush()
    
    async def get_list(
        self,
        page: int = 1,
        per_page: int = 20,
        category_id: Optional[int] = None,
        tag: Optional[str] = None,
        author_id: Optional[int] = None,
        search: Optional[str] = None,
        is_published: Optional[bool] = True,
        is_featured: Optional[bool] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> tuple[List[Post], int]:
        """Get paginated list of posts"""
        query = select(Post).options(
            selectinload(Post.author).selectinload(User.group),
            selectinload(Post.categories),
            selectinload(Post.tags),
        )
        count_query = select(func.count(Post.id))
        
        # Apply filters
        if is_published is not None:
            query = query.where(Post.is_published == is_published)
            count_query = count_query.where(Post.is_published == is_published)
        
        if is_featured is not None:
            query = query.where(Post.is_featured == is_featured)
            count_query = count_query.where(Post.is_featured == is_featured)
        
        if category_id:
            query = query.join(post_categories).where(
                post_categories.c.category_id == category_id
            )
            count_query = count_query.join(post_categories).where(
                post_categories.c.category_id == category_id
            )
        
        if tag:
            tag_subq = select(Tag.id).where(Tag.slug == tag)
            query = query.join(post_tags).where(
                post_tags.c.tag_id.in_(tag_subq)
            )
            count_query = count_query.join(post_tags).where(
                post_tags.c.tag_id.in_(tag_subq)
            )
        
        if author_id:
            query = query.where(Post.author_id == author_id)
            count_query = count_query.where(Post.author_id == author_id)
        
        if search:
            search_filter = or_(
                Post.title.ilike(f"%{search}%"),
                Post.short_content.ilike(f"%{search}%"),
                Post.full_content.ilike(f"%{search}%"),
            )
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)
        
        # Get total count
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Apply sorting
        sort_column = getattr(Post, sort_by, Post.created_at)
        if sort_order == "asc":
            query = query.order_by(Post.is_pinned.desc(), sort_column.asc())
        else:
            query = query.order_by(Post.is_pinned.desc(), sort_column.desc())
        
        # Apply pagination
        offset = (page - 1) * per_page
        query = query.offset(offset).limit(per_page)
        
        result = await self.db.execute(query)
        posts = list(result.scalars().unique().all())
        
        return posts, total
    
    async def increment_views(self, post: Post, user_id: Optional[int], ip: str, user_agent: str, referer: Optional[str] = None) -> None:
        """Track post view"""
        post.views_count += 1
        
        view = PostView(
            post_id=post.id,
            user_id=user_id,
            ip_address=ip,
            user_agent=user_agent[:255] if user_agent else None,
            referer=referer[:255] if referer else None,
        )
        self.db.add(view)
        await self.db.flush()
    
    async def rate_post(self, post: Post, rating: int, user_id: Optional[int], ip: str) -> tuple[float, int]:
        """Rate a post"""
        # Check if already rated
        existing = await self.db.execute(
            select(PostRating).where(
                PostRating.post_id == post.id,
                or_(
                    PostRating.user_id == user_id if user_id else False,
                    PostRating.ip_address == ip,
                )
            )
        )
        existing_rating = existing.scalar_one_or_none()
        
        if existing_rating:
            # Update existing rating
            old_rating = existing_rating.rating
            existing_rating.rating = rating
            post.rating = (
                (post.rating * post.votes_count - old_rating + rating) / post.votes_count
            )
        else:
            # Add new rating
            new_rating = PostRating(
                post_id=post.id,
                user_id=user_id,
                ip_address=ip,
                rating=rating,
            )
            self.db.add(new_rating)
            
            post.votes_count += 1
            post.rating = (
                (post.rating * (post.votes_count - 1) + rating) / post.votes_count
            )
        
        await self.db.flush()
        return post.rating, post.votes_count
    
    async def _set_categories(self, post: Post, category_ids: List[int]) -> None:
        """Set post categories"""
        result = await self.db.execute(
            select(Category).where(Category.id.in_(category_ids))
        )
        categories = list(result.scalars().all())
        post.categories = categories
    
    async def _set_tags(self, post: Post, tag_names: List[str]) -> None:
        """Set post tags, creating new ones if needed"""
        tags = []
        for name in tag_names:
            slug = slugify(name)
            result = await self.db.execute(
                select(Tag).where(Tag.slug == slug)
            )
            tag = result.scalar_one_or_none()
            
            if not tag:
                tag = Tag(name=name, slug=slug)
                self.db.add(tag)
                await self.db.flush()
            
            tags.append(tag)
        
        post.tags = tags
    
    async def get_popular(self, limit: int = 10) -> List[Post]:
        """Get popular posts by views"""
        result = await self.db.execute(
            select(Post)
            .options(selectinload(Post.author).selectinload(User.group), selectinload(Post.categories))
            .where(Post.is_published == True)
            .order_by(Post.views_count.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_recent(self, limit: int = 10) -> List[Post]:
        """Get recent posts"""
        result = await self.db.execute(
            select(Post)
            .options(selectinload(Post.author).selectinload(User.group), selectinload(Post.categories))
            .where(Post.is_published == True)
            .order_by(Post.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_featured(self, limit: int = 5) -> List[Post]:
        """Get featured posts"""
        result = await self.db.execute(
            select(Post)
            .options(selectinload(Post.author).selectinload(User.group), selectinload(Post.categories))
            .where(Post.is_published == True, Post.is_featured == True)
            .order_by(Post.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_related(self, post: Post, limit: int = 5) -> List[Post]:
        """Get related posts based on categories and tags"""
        category_ids = [c.id for c in post.categories]
        tag_ids = [t.id for t in post.tags]
        
        query = (
            select(Post)
            .options(selectinload(Post.author).selectinload(User.group), selectinload(Post.categories))
            .where(Post.id != post.id, Post.is_published == True)
        )
        
        if category_ids:
            query = query.join(post_categories).where(
                post_categories.c.category_id.in_(category_ids)
            )
        
        result = await self.db.execute(query.limit(limit))
        return list(result.scalars().unique().all())
