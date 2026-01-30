import asyncio
from sqlalchemy import select
from app.core.database import async_session_maker
from app.models.user import User
from app.core.security import hash_password

async def create_admin_user():
    async with async_session_maker() as session:
        # Check if admin exists
        result = await session.execute(select(User).where(User.username == "admin"))
        user = result.scalar_one_or_none()
        
        if user:
            print("Admin user already exists.")
        else:
            print("Creating admin user...")
            new_user = User(
                username="admin",
                email="admin@example.com",
                password_hash=hash_password("admin123"),
                full_name="Administrator",
                group_id=1,
                is_active=True,
                is_verified=True
            )
            session.add(new_user)
            await session.commit()
            print("Admin user created successfully.")
            print("Username: admin")
            print("Password: admin123")

if __name__ == "__main__":
    asyncio.run(create_admin_user())
