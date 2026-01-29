"""
Utility functions
"""
import os
import uuid
import aiofiles
from typing import Optional
from fastapi import UploadFile, HTTPException, status
from PIL import Image
from io import BytesIO

from app.core.config import settings


async def save_upload_file(
    file: UploadFile,
    folder: str = "uploads",
    allowed_types: Optional[list[str]] = None,
) -> str:
    """
    Save uploaded file and return the URL path
    """
    # Check file extension
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided",
        )
    
    ext = file.filename.split(".")[-1].lower()
    
    if allowed_types is None:
        allowed_types = settings.allowed_extensions_list
    
    if ext not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed: {', '.join(allowed_types)}",
        )
    
    # Check file size
    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Max size: {settings.MAX_UPLOAD_SIZE // 1024 // 1024}MB",
        )
    
    # Generate unique filename
    unique_name = f"{uuid.uuid4().hex}.{ext}"
    
    # Create directory if not exists
    upload_dir = os.path.join(settings.UPLOAD_DIR, folder)
    os.makedirs(upload_dir, exist_ok=True)
    
    # Save file
    file_path = os.path.join(upload_dir, unique_name)
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)
    
    # Return relative URL path
    return f"/uploads/{folder}/{unique_name}"


async def save_image(
    file: UploadFile,
    folder: str = "images",
    max_width: int = 1920,
    max_height: int = 1080,
    quality: int = 85,
) -> str:
    """
    Save and optimize uploaded image
    """
    allowed_types = ["jpg", "jpeg", "png", "gif", "webp"]
    
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided",
        )
    
    ext = file.filename.split(".")[-1].lower()
    
    if ext not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Image type not allowed. Allowed: {', '.join(allowed_types)}",
        )
    
    content = await file.read()
    
    # Open and optimize image
    img = Image.open(BytesIO(content))
    
    # Convert to RGB if necessary
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    
    # Resize if too large
    if img.width > max_width or img.height > max_height:
        img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
    
    # Generate unique filename
    unique_name = f"{uuid.uuid4().hex}.webp"
    
    # Create directory
    upload_dir = os.path.join(settings.UPLOAD_DIR, folder)
    os.makedirs(upload_dir, exist_ok=True)
    
    # Save optimized image
    file_path = os.path.join(upload_dir, unique_name)
    img.save(file_path, "WEBP", quality=quality, optimize=True)
    
    return f"/uploads/{folder}/{unique_name}"


async def create_thumbnail(
    source_path: str,
    width: int = 300,
    height: int = 200,
) -> str:
    """
    Create thumbnail from existing image
    """
    if not os.path.exists(source_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source image not found",
        )
    
    img = Image.open(source_path)
    
    # Convert to RGB
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")
    
    # Create thumbnail
    img.thumbnail((width, height), Image.Resampling.LANCZOS)
    
    # Generate filename
    unique_name = f"thumb_{uuid.uuid4().hex}.webp"
    thumb_dir = os.path.join(settings.UPLOAD_DIR, "thumbnails")
    os.makedirs(thumb_dir, exist_ok=True)
    
    thumb_path = os.path.join(thumb_dir, unique_name)
    img.save(thumb_path, "WEBP", quality=80)
    
    return f"/uploads/thumbnails/{unique_name}"


def delete_file(file_path: str) -> bool:
    """
    Delete file from filesystem
    """
    # Convert URL path to filesystem path
    if file_path.startswith("/uploads/"):
        file_path = file_path.replace("/uploads/", f"{settings.UPLOAD_DIR}/")
    
    if os.path.exists(file_path):
        os.remove(file_path)
        return True
    return False


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human readable format
    """
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"
