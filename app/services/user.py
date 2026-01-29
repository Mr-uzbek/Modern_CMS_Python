"""
User service - Business logic for user management
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.user import User, UserGroup
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import hash_password, verify_password


class UserService:
    """Service for user-related operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.group))
            .where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.group))
            .where(User.username == username)
        )
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.group))
            .where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_by_username_or_email(self, identifier: str) -> Optional[User]:
        """Get user by username or email"""
        result = await self.db.execute(
            select(User)
            .options(selectinload(User.group))
            .where(or_(User.username == identifier, User.email == identifier))
        )
        return result.scalar_one_or_none()
    
    async def create(self, data: UserCreate, group_id: int = 2) -> User:
        """Create new user"""
        user = User(
            username=data.username,
            email=data.email,
            password_hash=hash_password(data.password),
            full_name=data.full_name,
            group_id=group_id,
        )
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user
    
    async def update(self, user: User, data: UserUpdate) -> User:
        """Update user profile"""
        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        await self.db.flush()
        await self.db.refresh(user)
        return user
    
    async def change_password(
        self, user: User, current_password: str, new_password: str
    ) -> bool:
        """Change user password"""
        if not verify_password(current_password, user.password_hash):
            return False
        user.password_hash = hash_password(new_password)
        await self.db.flush()
        return True
    
    async def update_last_login(self, user: User, ip: str) -> None:
        """Update last login info"""
        user.last_login = datetime.utcnow()
        user.last_ip = ip
        await self.db.flush()
    
    async def ban_user(self, user: User, reason: str) -> None:
        """Ban a user"""
        user.is_banned = True
        user.ban_reason = reason
        await self.db.flush()
    
    async def unban_user(self, user: User) -> None:
        """Unban a user"""
        user.is_banned = False
        user.ban_reason = None
        await self.db.flush()
    
    async def verify_user(self, user: User) -> None:
        """Mark user as verified"""
        user.is_verified = True
        await self.db.flush()
    
    async def delete(self, user: User) -> None:
        """Delete user"""
        await self.db.delete(user)
        await self.db.flush()
    
    async def get_list(
        self,
        page: int = 1,
        per_page: int = 20,
        search: Optional[str] = None,
        group_id: Optional[int] = None,
        is_active: Optional[bool] = None,
    ) -> tuple[List[User], int]:
        """Get paginated list of users"""
        query = select(User).options(selectinload(User.group))
        count_query = select(func.count(User.id))
        
        # Apply filters
        if search:
            search_filter = or_(
                User.username.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%"),
                User.full_name.ilike(f"%{search}%"),
            )
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)
        
        if group_id is not None:
            query = query.where(User.group_id == group_id)
            count_query = count_query.where(User.group_id == group_id)
        
        if is_active is not None:
            query = query.where(User.is_active == is_active)
            count_query = count_query.where(User.is_active == is_active)
        
        # Get total count
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Apply pagination
        offset = (page - 1) * per_page
        query = query.order_by(User.created_at.desc()).offset(offset).limit(per_page)
        
        result = await self.db.execute(query)
        users = list(result.scalars().all())
        
        return users, total
    
    async def authenticate(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username/email and password"""
        user = await self.get_by_username_or_email(username)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        if not user.is_active or user.is_banned:
            return None
        return user
    
    async def increment_posts_count(self, user: User) -> None:
        """Increment user's posts count"""
        user.posts_count += 1
        await self.db.flush()
    
    async def increment_comments_count(self, user: User) -> None:
        """Increment user's comments count"""
        user.comments_count += 1
        await self.db.flush()


class UserGroupService:
    """Service for user group operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, group_id: int) -> Optional[UserGroup]:
        """Get group by ID"""
        result = await self.db.execute(
            select(UserGroup).where(UserGroup.id == group_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self) -> List[UserGroup]:
        """Get all groups"""
        result = await self.db.execute(
            select(UserGroup).order_by(UserGroup.id)
        )
        return list(result.scalars().all())
    
    async def create(self, data: dict) -> UserGroup:
        """Create new group"""
        group = UserGroup(**data)
        self.db.add(group)
        await self.db.flush()
        await self.db.refresh(group)
        return group
    
    async def create_default_groups(self) -> None:
        """Create default user groups"""
        groups = [
            {
                "id": 1,
                "name": "Administrator",
                "can_add_posts": True,
                "can_edit_posts": True,
                "can_delete_posts": True,
                "can_add_comments": True,
                "can_edit_comments": True,
                "can_delete_comments": True,
                "can_upload_files": True,
                "can_access_admin": True,
                "is_admin": True,
                "max_file_size": 52428800,
                "max_posts_per_day": 1000,
            },
            {
                "id": 2,
                "name": "User",
                "can_add_posts": False,
                "can_edit_posts": False,
                "can_delete_posts": False,
                "can_add_comments": True,
                "can_edit_comments": False,
                "can_delete_comments": False,
                "can_upload_files": False,
                "can_access_admin": False,
                "is_admin": False,
            },
            {
                "id": 3,
                "name": "Editor",
                "can_add_posts": True,
                "can_edit_posts": True,
                "can_delete_posts": False,
                "can_add_comments": True,
                "can_edit_comments": True,
                "can_delete_comments": False,
                "can_upload_files": True,
                "can_access_admin": True,
                "is_admin": False,
                "max_file_size": 10485760,
                "max_posts_per_day": 50,
            },
            {
                "id": 4,
                "name": "Moderator",
                "can_add_posts": True,
                "can_edit_posts": True,
                "can_delete_posts": True,
                "can_add_comments": True,
                "can_edit_comments": True,
                "can_delete_comments": True,
                "can_upload_files": True,
                "can_access_admin": True,
                "is_admin": False,
                "max_file_size": 20971520,
                "max_posts_per_day": 100,
            },
        ]
        
        for group_data in groups:
            existing = await self.get_by_id(group_data["id"])
            if not existing:
                await self.create(group_data)
