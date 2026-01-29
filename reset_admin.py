import asyncio
from sqlalchemy import select
from app.core.database import async_session_maker
from app.models.user import User
from app.core.security import hash_password

async def reset_admin_password():
    async with async_session_maker() as session:
        result = await session.execute(select(User).where(User.username == "admin"))
        user = result.scalar_one_or_none()
        if user:
            user.password_hash = hash_password("admin123")
            await session.commit()
            print("Admin password reset to 'admin123'")
        else:
            print("Admin user not found")

if __name__ == "__main__":
    asyncio.run(reset_admin_password())
