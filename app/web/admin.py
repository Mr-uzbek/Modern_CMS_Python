"""
Admin Routes - Admin panel pages
"""
from fastapi import APIRouter, Depends, Request, Form, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select

from app.core.database import get_db
from app.models import User, Post, Comment
from app.services.user import UserService
from app.services.post import PostService
from app.services.category import CategoryService
from app.services.comment import CommentService
from app.services.cms import SettingService, StaticPageService


router = APIRouter(prefix="/admin")
templates = Jinja2Templates(directory="templates")


async def get_admin_user(request: Request, db: AsyncSession):
    """Get current admin user or redirect"""
    from app.web.routes import get_current_user_from_cookie
    user = await get_current_user_from_cookie(request, db)
    if not user or not user.group or not user.group.can_access_admin:
        return None
    return user


async def require_admin(request: Request, db: AsyncSession):
    user = await get_admin_user(request, db)
    if not user:
        raise HTTPException(status_code=302, headers={"Location": "/login"})
    return user


# ========== DASHBOARD ==========

@router.get("", response_class=HTMLResponse)
async def admin_dashboard(request: Request, db: AsyncSession = Depends(get_db)):
    """Admin dashboard"""
    current_user = await get_admin_user(request, db)
    if not current_user:
        return RedirectResponse("/login", status_code=302)
    
    # Get stats
    posts_count = await db.scalar(select(func.count(Post.id)))
    users_count = await db.scalar(select(func.count(User.id)))
    comments_count = await db.scalar(select(func.count(Comment.id)))
    views_count = await db.scalar(select(func.sum(Post.views_count))) or 0
    
    # Recent posts
    post_service = PostService(db)
    recent_posts, _ = await post_service.get_list(page=1, per_page=5, is_published=None)
    
    # Recent comments
    comment_service = CommentService(db)
    recent_comments = await comment_service.get_latest(5)
    
    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request,
        "current_user": current_user,
        "active": "dashboard",
        "stats": {
            "posts_count": posts_count,
            "users_count": users_count,
            "comments_count": comments_count,
            "views_count": views_count,
        },
        "recent_posts": recent_posts,
        "recent_comments": recent_comments,
    })


# ========== POSTS ==========

@router.get("/posts", response_class=HTMLResponse)
async def admin_posts(request: Request, page: int = 1, db: AsyncSession = Depends(get_db)):
    """Posts list"""
    current_user = await get_admin_user(request, db)
    if not current_user:
        return RedirectResponse("/login", status_code=302)
    
    post_service = PostService(db)
    posts, total = await post_service.get_list(page=page, per_page=20, is_published=None)
    total_pages = (total + 19) // 20
    
    return templates.TemplateResponse("admin/posts.html", {
        "request": request,
        "current_user": current_user,
        "active": "posts",
        "posts": posts,
        "page": page,
        "total_pages": total_pages,
    })


@router.get("/posts/new", response_class=HTMLResponse)
async def admin_post_new(request: Request, db: AsyncSession = Depends(get_db)):
    """New post form"""
    current_user = await get_admin_user(request, db)
    if not current_user:
        return RedirectResponse("/login", status_code=302)
    
    cat_service = CategoryService(db)
    categories = await cat_service.get_all()
    
    return templates.TemplateResponse("admin/post_form.html", {
        "request": request,
        "current_user": current_user,
        "active": "posts",
        "post": None,
        "categories": categories,
    })


@router.post("/posts/new")
async def admin_post_create(
    request: Request,
    title: str = Form(...),
    short_content: str = Form(""),
    full_content: str = Form(...),
    is_published: str = Form(None),
    is_featured: str = Form(None),
    category_ids: list = Form([]),
    tags: str = Form(""),
    meta_title: str = Form(""),
    meta_description: str = Form(""),
    thumbnail: UploadFile = File(None),
    db: AsyncSession = Depends(get_db),
):
    """Create post"""
    current_user = await get_admin_user(request, db)
    if not current_user:
        return RedirectResponse("/login", status_code=302)
    
    from app.schemas.post import PostCreate
    
    # Parse checkbox values (HTML sends "on" when checked)
    published = is_published is not None
    featured = is_featured is not None
    
    # Parse tags
    tag_list = [t.strip() for t in tags.split(",") if t.strip()]
    
    # Handle thumbnail
    thumbnail_url = None
    if thumbnail and thumbnail.filename:
        from app.utils.files import save_upload_file
        thumbnail_url = await save_upload_file(thumbnail, "posts")
    
    post_data = PostCreate(
        title=title,
        short_content=short_content,
        full_content=full_content,
        is_published=published,
        is_featured=featured,
        category_ids=category_ids if isinstance(category_ids, list) else [int(category_ids)] if category_ids else [],
        tags=tag_list,
        thumbnail=thumbnail_url,
        meta_title=meta_title,
        meta_description=meta_description,
    )
    
    post_service = PostService(db)
    await post_service.create(post_data, author_id=current_user.id)
    
    return RedirectResponse("/admin/posts", status_code=302)


@router.get("/posts/{post_id}/edit", response_class=HTMLResponse)
async def admin_post_edit(post_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    """Edit post form"""
    current_user = await get_admin_user(request, db)
    if not current_user:
        return RedirectResponse("/login", status_code=302)
    
    post_service = PostService(db)
    post = await post_service.get_by_id(post_id)
    
    if not post:
        raise HTTPException(status_code=404)
    
    cat_service = CategoryService(db)
    categories = await cat_service.get_all()
    
    return templates.TemplateResponse("admin/post_form.html", {
        "request": request,
        "current_user": current_user,
        "active": "posts",
        "post": post,
        "categories": categories,
    })


@router.post("/posts/{post_id}/delete")
async def admin_post_delete(post_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    """Delete post"""
    current_user = await get_admin_user(request, db)
    if not current_user:
        return RedirectResponse("/login", status_code=302)
    
    post_service = PostService(db)
    post = await post_service.get_by_id(post_id)
    
    if post:
        await post_service.delete(post)
    
    return RedirectResponse("/admin/posts", status_code=302)


# ========== USERS ==========

@router.get("/users", response_class=HTMLResponse)
async def admin_users(request: Request, page: int = 1, db: AsyncSession = Depends(get_db)):
    """Users list"""
    current_user = await get_admin_user(request, db)
    if not current_user:
        return RedirectResponse("/login", status_code=302)
    
    user_service = UserService(db)
    users, total = await user_service.get_list(page=page, per_page=20)
    
    return templates.TemplateResponse("admin/users.html", {
        "request": request,
        "current_user": current_user,
        "active": "users",
        "users": users,
        "page": page,
        "total_pages": (total + 19) // 20,
    })


# ========== COMMENTS ==========

@router.get("/comments", response_class=HTMLResponse)
async def admin_comments(request: Request, page: int = 1, db: AsyncSession = Depends(get_db)):
    """Comments moderation"""
    current_user = await get_admin_user(request, db)
    if not current_user:
        return RedirectResponse("/login", status_code=302)
    
    comment_service = CommentService(db)
    comments = await comment_service.get_latest(50)
    
    return templates.TemplateResponse("admin/comments.html", {
        "request": request,
        "current_user": current_user,
        "active": "comments",
        "comments": comments,
    })


@router.post("/comments/{comment_id}/approve")
async def admin_comment_approve(comment_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    current_user = await get_admin_user(request, db)
    if not current_user:
        return RedirectResponse("/login", status_code=302)
    
    comment_service = CommentService(db)
    comment = await comment_service.get_by_id(comment_id)
    if comment:
        await comment_service.approve(comment)
    
    return RedirectResponse("/admin/comments", status_code=302)


@router.post("/comments/{comment_id}/delete")
async def admin_comment_delete(comment_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    current_user = await get_admin_user(request, db)
    if not current_user:
        return RedirectResponse("/login", status_code=302)
    
    comment_service = CommentService(db)
    comment = await comment_service.get_by_id(comment_id)
    if comment:
        await comment_service.delete(comment)
    
    return RedirectResponse("/admin/comments", status_code=302)


# ========== CATEGORIES ==========

@router.get("/categories", response_class=HTMLResponse)
async def admin_categories(request: Request, db: AsyncSession = Depends(get_db)):
    """Categories management"""
    current_user = await get_admin_user(request, db)
    if not current_user:
        return RedirectResponse("/login", status_code=302)
    
    cat_service = CategoryService(db)
    categories = await cat_service.get_all()
    
    return templates.TemplateResponse("admin/categories.html", {
        "request": request,
        "current_user": current_user,
        "active": "categories",
        "categories": categories,
    })


# ========== SETTINGS ==========

@router.get("/settings", response_class=HTMLResponse)
async def admin_settings(request: Request, db: AsyncSession = Depends(get_db)):
    """Site settings"""
    current_user = await get_admin_user(request, db)
    if not current_user:
        return RedirectResponse("/login", status_code=302)
    
    service = SettingService(db)
    db_settings = await service.get_all()
    
    # Defaults
    settings = {
        "site_name": "Modern CMS",
        "site_description": "FastAPI based CMS",
        "contact_email": "admin@example.com",
        "allow_registration": "True",
        "meta_description": "",
        "meta_keywords": "",
        "google_analytics": "",
        "social_telegram": "",
        "social_instagram": "",
        "social_youtube": "",
    }
    
    # Override with DB values
    for s in db_settings:
        settings[s.key] = s.value
    
    return templates.TemplateResponse("admin/settings.html", {
        "request": request,
        "current_user": current_user,
        "active": "settings",
        "settings": settings,
    })


@router.post("/settings")
async def admin_settings_save(request: Request, db: AsyncSession = Depends(get_db)):
    """Save settings"""
    current_user = await get_admin_user(request, db)
    if not current_user:
        return RedirectResponse("/login", status_code=302)
    
    form_data = await request.form()
    service = SettingService(db)
    
    for key, value in form_data.items():
        # Skip internal form fields
        if key in ["request"]: continue
        await service.set_value(key, str(value))
    
    await db.commit()
    return RedirectResponse("/admin/settings", status_code=302)


# ========== PAGES ==========

@router.get("/pages", response_class=HTMLResponse)
async def admin_pages(request: Request, db: AsyncSession = Depends(get_db)):
    """Static pages management"""
    current_user = await get_admin_user(request, db)
    if not current_user:
        return RedirectResponse("/login", status_code=302)
    
    service = StaticPageService(db)
    pages = await service.get_all()
    
    return templates.TemplateResponse("admin/pages.html", {
        "request": request,
        "current_user": current_user,
        "active": "pages",
        "pages": pages,
    })


@router.post("/pages/new")
async def admin_page_create(
    request: Request,
    title: str = Form(...),
    name: str = Form(...),
    content: str = Form(...),
    is_active: str = Form(None),
    db: AsyncSession = Depends(get_db),
):
    """Create static page"""
    current_user = await get_admin_user(request, db)
    if not current_user:
        return RedirectResponse("/login", status_code=302)
    
    service = StaticPageService(db)
    await service.create(
        name=name,
        title=title,
        content=content,
        is_active=bool(is_active)
    )
    await db.commit()
    
    return RedirectResponse("/admin/pages", status_code=302)

