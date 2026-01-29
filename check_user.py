import asyncio
from sqlalchemy import select
from app.core.database import async_session_maker
from app.models.user import User

async def check_user():
    async with async_session_maker() as session:
        result = await session.execute(select(User).where(User.username == "admin"))
        user = result.scalar_one_or_none()
        if user:
            print(f"User: {user.username}")
            print(f"Avatar type: {type(user.avatar)}")
            print(f"Avatar value: {repr(user.avatar)}")
        else:
            print("Admin user not found")

if __name__ == "__main__":
    asyncio.run(check_user())
