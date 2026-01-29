"""
CMS Service for settings and static pages
"""
from typing import List, Optional, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.cms import Setting, StaticPage
from slugify import slugify

class SettingService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, group: Optional[str] = None) -> List[Setting]:
        query = select(Setting)
        if group:
            query = query.where(Setting.group == group)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_value(self, key: str, default: Any = None) -> Any:
        result = await self.db.execute(select(Setting).where(Setting.key == key))
        setting = result.scalar_one_or_none()
        if not setting:
            return default
        
        if setting.type == "int":
            return int(setting.value) if setting.value else default
        elif setting.type == "bool":
            return setting.value.lower() == "true" if setting.value else default
        return setting.value

    async def set_value(self, key: str, value: str, group: str = "general", setting_type: str = "string"):
        result = await self.db.execute(select(Setting).where(Setting.key == key))
        setting = result.scalar_one_or_none()
        
        if setting:
            setting.value = str(value)
        else:
            setting = Setting(key=key, value=str(value), group=group, type=setting_type)
            self.db.add(setting)
        
        await self.db.flush()
        return setting

class StaticPageService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, active_only: bool = False) -> List[StaticPage]:
        query = select(StaticPage)
        if active_only:
            query = query.where(StaticPage.is_active == True)
        query = query.order_by(StaticPage.menu_position)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_by_id(self, page_id: int) -> Optional[StaticPage]:
        result = await self.db.execute(select(StaticPage).where(StaticPage.id == page_id))
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Optional[StaticPage]:
        result = await self.db.execute(select(StaticPage).where(StaticPage.slug == slug))
        return result.scalar_one_or_none()

    async def create(self, name: str, title: str, content: str, is_active: bool = True):
        slug = slugify(name)
        page = StaticPage(
            name=name,
            slug=slug,
            title=title,
            content=content,
            is_active=is_active
        )
        self.db.add(page)
        await self.db.flush()
        return page

    async def update(self, page_id: int, **kwargs):
        page = await self.get_by_id(page_id)
        if not page:
            return None
        
        for key, value in kwargs.items():
            if hasattr(page, key):
                setattr(page, key, value)
        
        await self.db.flush()
        return page
