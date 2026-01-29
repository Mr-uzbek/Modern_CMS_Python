"""
Frontend Routes - Web pages with Jinja2 templates
"""
from typing import Optional
from fastapi import APIRouter, Depends, Request, Form, HTTPException, status, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import create_access_token, create_refresh_token
from app.services.user import UserService
from app.services.post import PostService
from app.services.category import CategoryService, TagService
from app.services.comment import CommentService


router = APIRouter()
templates = Jinja2Templates(directory="templates")


# Helper to get current user from cookie
async def get_current_user_from_cookie(request: Request, db: AsyncSession):
    token = request.cookies.get("access_token")
    if not token:
        return None
    from app.core.security import verify_token
    payload = verify_token(token)
    if not payload:
        return None
    user_id = payload.get("sub")
    if not user_id:
        return None
    service = UserService(db)
    return await service.get_by_id(int(user_id))


async def get_common_context(request: Request, db: AsyncSession):
    """Get common template context"""
    current_user = await get_current_user_from_cookie(request, db)
    cat_service = CategoryService(db)
    categories = await cat_service.get_menu_categories()
    return {
        "request": request,
        "current_user": current_user,
        "categories": categories,
    }


# ========== PUBLIC PAGES ==========

@router.get("/", response_class=HTMLResponse)
async def home(request: Request, page: int = 1, db: AsyncSession = Depends(get_db)):
    """Homepage"""
    context = await get_common_context(request, db)
    
    post_service = PostService(db)
    tag_service = TagService(db)
    
    # Get featured post
    featured = await post_service.get_featured(1)
    featured_post = featured[0] if featured else None
    
    # Get posts
    posts, total = await post_service.get_list(page=page, per_page=9)
    total_pages = (total + 8) // 9
    
    # Get popular posts
    popular_posts = await post_service.get_popular(5)
    
    # Get tags
    tags = await tag_service.get_popular(15)
    
    context.update({
        "active_page": "home",
        "featured_post": featured_post,
        "posts": posts,
        "popular_posts": popular_posts,
        "tags": tags,
        "page": page,
        "total_pages": total_pages,
    })
    
    return templates.TemplateResponse("home.html", context)


@router.get("/post/{slug}", response_class=HTMLResponse)
async def post_detail(slug: str, request: Request, db: AsyncSession = Depends(get_db)):
    """Post detail page"""
    context = await get_common_context(request, db)
    
    post_service = PostService(db)
    post = await post_service.get_by_slug(slug)
    
    if not post or not post.is_published:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Increment views
    ip = request.client.host if request.client else "unknown"
    user_id = context["current_user"].id if context["current_user"] else None
    await post_service.increment_views(post, user_id, ip, request.headers.get("User-Agent", ""))
    
    # Get comments
    comment_service = CommentService(db)
    comments, _ = await comment_service.get_by_post(post.id)
    
    # Get related posts
    related_posts = await post_service.get_related(post, 5)
    
    # Get tags
    tag_service = TagService(db)
    tags = await tag_service.get_popular(15)
    
    context.update({
        "post": post,
        "comments": comments,
        "related_posts": related_posts,
        "tags": tags,
    })
    
    return templates.TemplateResponse("post_detail.html", context)


@router.get("/category/{slug}", response_class=HTMLResponse)
async def category_page(slug: str, request: Request, page: int = 1, db: AsyncSession = Depends(get_db)):
    """Category posts page"""
    context = await get_common_context(request, db)
    
    cat_service = CategoryService(db)
    category = await cat_service.get_by_slug(slug)
    
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    
    post_service = PostService(db)
    posts, total = await post_service.get_list(page=page, per_page=12, category_id=category.id)
    total_pages = (total + 11) // 12
    
    context.update({
        "category": category,
        "posts": posts,
        "page": page,
        "total_pages": total_pages,
    })
    
    return templates.TemplateResponse("category.html", context)


@router.get("/tag/{slug}", response_class=HTMLResponse)
async def tag_page(slug: str, request: Request, page: int = 1, db: AsyncSession = Depends(get_db)):
    """Tag posts page"""
    context = await get_common_context(request, db)
    
    tag_service = TagService(db)
    tag = await tag_service.get_by_slug(slug)
    
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    post_service = PostService(db)
    posts, total = await post_service.get_list(page=page, per_page=12, tag=slug)
    
    context.update({
        "tag": tag,
        "posts": posts,
        "page": page,
        "total_pages": (total + 11) // 12,
    })
    
    return templates.TemplateResponse("tag.html", context)


@router.get("/search", response_class=HTMLResponse)
async def search_page(request: Request, q: str = "", page: int = 1, db: AsyncSession = Depends(get_db)):
    """Search results page"""
    context = await get_common_context(request, db)
    
    posts = []
    total = 0
    
    if q:
        post_service = PostService(db)
        posts, total = await post_service.get_list(page=page, per_page=12, search=q)
    
    context.update({
        "query": q,
        "posts": posts,
        "total": total,
        "page": page,
        "total_pages": (total + 11) // 12,
    })
    
    return templates.TemplateResponse("search.html", context)


# ========== CATEGORIES & TAGS PAGES ==========

@router.get("/categories", response_class=HTMLResponse)
async def categories_page(request: Request, db: AsyncSession = Depends(get_db)):
    """All categories page"""
    context = await get_common_context(request, db)
    
    cat_service = CategoryService(db)
    all_categories = await cat_service.get_all()
    
    context.update({
        "all_categories": all_categories,
    })
    
    return templates.TemplateResponse("categories.html", context)


@router.get("/tags", response_class=HTMLResponse)
async def tags_page(request: Request, db: AsyncSession = Depends(get_db)):
    """All tags page"""
    context = await get_common_context(request, db)
    
    tag_service = TagService(db)
    all_tags = await tag_service.get_all()
    
    context.update({
        "all_tags": all_tags,
    })
    
    return templates.TemplateResponse("tags.html", context)


# ========== PROFILE PAGE ==========

@router.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request, db: AsyncSession = Depends(get_db)):
    """User profile page"""
    context = await get_common_context(request, db)
    
    if not context["current_user"]:
        return RedirectResponse("/login", status_code=302)
    
    # Get user posts
    post_service = PostService(db)
    user_posts, total = await post_service.get_list(
        page=1, per_page=10, author_id=context["current_user"].id
    )
    
    context.update({
        "user_posts": user_posts,
        "total_posts": total,
    })
    
    return templates.TemplateResponse("profile.html", context)


@router.post("/profile/update")
async def profile_update(
    request: Request,
    full_name: str = Form(None),
    bio: str = Form(None),
    website: str = Form(None),
    telegram: str = Form(None),
    avatar: UploadFile = File(None),
    db: AsyncSession = Depends(get_db),
):
    """Update user profile"""
    current_user = await get_current_user_from_cookie(request, db)
    if not current_user:
        return RedirectResponse("/login", status_code=302)
    
    avatar_url = current_user.avatar
    if avatar and avatar.filename:
        from app.utils.files import save_upload_file
        avatar_url = await save_upload_file(avatar, "avatars")
    
    user_service = UserService(db)
    from app.schemas.user import UserUpdate
    
    update_data = UserUpdate(
        full_name=full_name,
        bio=bio,
        website=website,
        telegram=telegram,
        avatar=avatar_url
    )
    
    await user_service.update(current_user, update_data)
    await db.commit()
    
    return RedirectResponse("/profile", status_code=302)


# ========== AUTH PAGES ==========

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, db: AsyncSession = Depends(get_db)):
    """Login page"""
    context = await get_common_context(request, db)
    if context["current_user"]:
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse("auth/login.html", context)


@router.post("/login", response_class=HTMLResponse)
async def login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    remember_me: bool = Form(False),
    db: AsyncSession = Depends(get_db),
):
    """Login form submission"""
    context = await get_common_context(request, db)
    
    user_service = UserService(db)
    user = await user_service.authenticate(username, password)
    
    if not user:
        context["error"] = "Noto'g'ri foydalanuvchi nomi yoki parol"
        return templates.TemplateResponse("auth/login.html", context)
    
    # Update last login
    ip = request.client.host if request.client else "unknown"
    await user_service.update_last_login(user, ip)
    
    # Create tokens
    token_data = {"sub": str(user.id), "username": user.username}
    access_token = create_access_token(token_data)
    
    response = RedirectResponse("/", status_code=302)
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=86400 * 7 if remember_me else 3600,
    )
    return response


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request, db: AsyncSession = Depends(get_db)):
    """Register page"""
    context = await get_common_context(request, db)
    if context["current_user"]:
        return RedirectResponse("/", status_code=302)
    return templates.TemplateResponse("auth/register.html", context)


@router.post("/register", response_class=HTMLResponse)
async def register_submit(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    password2: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    """Register form submission"""
    context = await get_common_context(request, db)
    
    if password != password2:
        context["error"] = "Parollar mos kelmadi"
        return templates.TemplateResponse("auth/register.html", context)
    
    user_service = UserService(db)
    
    # Check if exists
    if await user_service.get_by_username(username):
        context["error"] = "Bu foydalanuvchi nomi band"
        return templates.TemplateResponse("auth/register.html", context)
    
    if await user_service.get_by_email(email):
        context["error"] = "Bu email allaqachon ro'yxatdan o'tgan"
        return templates.TemplateResponse("auth/register.html", context)
    
    # Create user
    from app.schemas.user import UserCreate
    user_data = UserCreate(username=username, email=email, password=password)
    user = await user_service.create(user_data)
    
    # Auto login
    token_data = {"sub": str(user.id), "username": user.username}
    access_token = create_access_token(token_data)
    
    response = RedirectResponse("/", status_code=302)
    response.set_cookie(key="access_token", value=access_token, httponly=True, max_age=3600)
    return response


@router.get("/logout")
async def logout():
    """Logout"""
    response = RedirectResponse("/", status_code=302)
    response.delete_cookie("access_token")
    return response


# ========== COMMENT SUBMISSION ==========

@router.post("/post/{post_id}/comment")
async def submit_comment(
    post_id: int,
    request: Request,
    content: str = Form(...),
    parent_id: Optional[int] = Form(None),
    db: AsyncSession = Depends(get_db),
):
    """Submit comment"""
    current_user = await get_current_user_from_cookie(request, db)
    
    if not current_user:
        return RedirectResponse(f"/login?next=/post/{post_id}", status_code=302)
    
    # Get post
    post_service = PostService(db)
    post = await post_service.get_by_id(post_id)
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Create comment
    comment_service = CommentService(db)
    from app.schemas.comment import CommentCreate
    comment_data = CommentCreate(content=content, post_id=post_id, parent_id=parent_id)
    
    ip = request.client.host if request.client else "unknown"
    await comment_service.create(comment_data, author_id=current_user.id, ip=ip)
    
    # Update post comments count
    post.comments_count += 1
    
    return RedirectResponse(f"/post/{post.slug}#comments", status_code=302)
