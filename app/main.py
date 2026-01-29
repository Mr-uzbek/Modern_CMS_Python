"""
Modern CMS - FastAPI Application
A modern, fast, and secure content management system built with Python.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import time

from app.core.config import settings
from app.core.database import init_db, engine
from app.api.v1 import router as api_router
from app.web.routes import router as web_router
from app.web.admin import router as admin_router
from app.services.user import UserGroupService
from app.core.database import async_session_maker


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan - startup and shutdown events"""
    # Startup
    print("🚀 Starting Modern CMS...")
    
    # Initialize database
    await init_db()
    print("✅ Database initialized")
    
    # Create default user groups
    async with async_session_maker() as session:
        group_service = UserGroupService(session)
        await group_service.create_default_groups()
        await session.commit()
    print("✅ Default user groups created")
    
    print(f"🌐 API Documentation: http://localhost:8000/docs")
    print(f"📚 ReDoc: http://localhost:8000/redoc")
    
    yield
    
    # Shutdown
    print("👋 Shutting down...")
    await engine.dispose()


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    ## Modern CMS API
    
    A modern, fast, and secure content management system built with Python and FastAPI.
    
    ### Features
    - 🔐 JWT Authentication with refresh tokens
    - 👥 User management with groups and permissions
    - 📝 Posts with categories, tags, and SEO
    - 💬 Nested comments with voting
    - 📊 View tracking and analytics
    - ⚡ Async database operations
    - 🔍 Full-text search support
    
    ### Authentication
    Most endpoints require authentication. Use the `/auth/login` endpoint to get tokens.
    """,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)


# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else ["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.4f}"
    return response


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    if settings.DEBUG:
        import traceback
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "detail": str(exc),
                "traceback": traceback.format_exc(),
            },
        )
    return JSONResponse(
        status_code=500,
        content={"error": "Internal Server Error"},
    )


# Include API router
app.include_router(api_router, prefix="/api")

# Include Web frontend routes
app.include_router(web_router)

# Include Admin panel routes
app.include_router(admin_router)


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "app": settings.APP_NAME,
    }


# Mount static files (if directory exists)
import os
if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

if os.path.exists("uploads"):
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
