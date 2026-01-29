import asyncio
from sqlalchemy import select
from app.core.database import async_session_maker
from app.models.post import Post

async def check_posts():
    async with async_session_maker() as session:
        result = await session.execute(select(Post))
        posts = result.scalars().all()
        print(f"Total posts: {len(posts)}")
        for post in posts[:3]:
            print(f"ID: {post.id}, Title: {post.title}")

if __name__ == "__main__":
    asyncio.run(check_posts())
