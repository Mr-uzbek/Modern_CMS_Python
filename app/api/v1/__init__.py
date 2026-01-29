"""
API v1 Router - Combines all API routes
"""
from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.users import router as users_router
from app.api.v1.posts import router as posts_router
from app.api.v1.categories import router as categories_router
from app.api.v1.comments import router as comments_router


router = APIRouter(prefix="/v1")

# Include all routers
router.include_router(auth_router)
router.include_router(users_router)
router.include_router(posts_router)
router.include_router(categories_router)
router.include_router(comments_router)
