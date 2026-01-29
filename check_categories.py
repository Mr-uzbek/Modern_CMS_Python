import asyncio
from sqlalchemy import select
from app.core.database import async_session_maker
from app.models.category import Category

async def check_categories():
    async with async_session_maker() as session:
        result = await session.execute(select(Category))
        categories = result.scalars().all()
        for cat in categories:
            print(f"ID: {cat.id}, Name: {cat.name}, Show in menu: {cat.show_in_menu}, Active: {cat.is_active}")

if __name__ == "__main__":
    asyncio.run(check_categories())
