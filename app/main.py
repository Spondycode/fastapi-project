from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, Form
from pydantic import BaseModel
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import os
import uuid
from pathlib import Path

from app.db import init_db, get_db
from app.models import Post
from app.images import upload_to_imagekit


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    await init_db()
    yield


app = FastAPI(
    title="FastAPI Project",
    description="A simple FastAPI application",
    version="0.1.0",
    lifespan=lifespan
)




@app.get("/")
async def root():
    """Root endpoint returning a welcome message."""
    return {"message": "Welcome to FastAPI!"}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/items/{item_id}")
async def read_item(item_id: str, db: AsyncSession = Depends(get_db)):
    """Get a specific post by ID."""
    try:
        post_uuid = uuid.UUID(item_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    
    result = await db.execute(select(Post).where(Post.id == post_uuid))
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    return {
        "id": str(post.id),
        "filename": post.file_name,
        "file_type": post.file_type,
        "url": post.url,
        "caption": post.caption,
        "created_at": post.created_at.isoformat()
    }


@app.get("/items/")
async def read_items(db: AsyncSession = Depends(get_db)):
    """Get all posts from database ordered by creation date (newest first)."""
    result = await db.execute(select(Post).order_by(Post.created_at.desc()))
    posts = result.scalars().all()
    
    items = [
        {
            "id": str(post.id),
            "filename": post.file_name,
            "file_type": post.file_type,
            "url": post.url,
            "caption": post.caption,
            "created_at": post.created_at.isoformat()
        }
        for post in posts
    ]
    
    return {"items": items, "total": len(items)}




@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    caption: str | None = Form(None),
    db: AsyncSession = Depends(get_db)
):
    """Upload a file to ImageKit and create a post record."""
    # Upload to ImageKit
    upload_result = await upload_to_imagekit(file)
    
    # Create database record with ImageKit URL
    new_post = Post(
        url=upload_result.url,
        file_type=file.content_type or "unknown",
        file_name=file.filename,
        caption=caption
    )
    
    db.add(new_post)
    await db.commit()
    await db.refresh(new_post)
    
    return {
        "id": str(new_post.id),
        "filename": new_post.file_name,
        "file_type": new_post.file_type,
        "url": new_post.url,
        "caption": new_post.caption,
        "created_at": new_post.created_at.isoformat()
    }


@app.delete("/items/{item_id}")
async def delete_item(item_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a specific post by ID."""
    try:
        post_uuid = uuid.UUID(item_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    
    result = await db.execute(select(Post).where(Post.id == post_uuid))
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    await db.delete(post)
    await db.commit()
    
    return {"message": "Post deleted successfully", "id": str(post_uuid)}
