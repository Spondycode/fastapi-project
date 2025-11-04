from fastapi import FastAPI, HTTPException, UploadFile, File, Depends, Form, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import os
import uuid
from pathlib import Path
from datetime import timedelta

from app.db import init_db, get_db
from app.models import Post, User
from app.images import upload_to_imagekit
from app.auth import (
    hash_password,
    authenticate_user,
    create_access_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.schemas import UserCreate, UserResponse, Token


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

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Narrow this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Frontend directory relative to this file (app/main.py)
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

# Mount static assets
if FRONTEND_DIR.exists():
    app.mount(
        "/frontend",
        StaticFiles(directory=str(FRONTEND_DIR)),
        name="frontend",
    )




@app.get("/", include_in_schema=False)
async def root():
    """Serve the frontend HTML page."""
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    return {"message": "Frontend not found. Build and place files in the frontend directory."}


@app.get("/index.html", include_in_schema=False)
async def index_page():
    """Serve the index page."""
    index_file = FRONTEND_DIR / "index.html"
    if index_file.exists():
        return FileResponse(str(index_file))
    raise HTTPException(status_code=404, detail="Page not found")


@app.get("/post.html", include_in_schema=False)
async def post_page():
    """Serve the post detail page."""
    post_file = FRONTEND_DIR / "post.html"
    if post_file.exists():
        return FileResponse(str(post_file))
    raise HTTPException(status_code=404, detail="Page not found")


@app.get("/upload.html", include_in_schema=False)
async def upload_page():
    """Serve the upload page."""
    upload_file = FRONTEND_DIR / "upload.html"
    if upload_file.exists():
        return FileResponse(str(upload_file))
    raise HTTPException(status_code=404, detail="Page not found")


@app.get("/login.html", include_in_schema=False)
async def login_page():
    """Serve the login page."""
    login_file = FRONTEND_DIR / "login.html"
    if login_file.exists():
        return FileResponse(str(login_file))
    raise HTTPException(status_code=404, detail="Page not found")


@app.get("/register.html", include_in_schema=False)
async def register_page():
    """Serve the register page."""
    register_file = FRONTEND_DIR / "register.html"
    if register_file.exists():
        return FileResponse(str(register_file))
    raise HTTPException(status_code=404, detail="Page not found")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# ============ Authentication Endpoints ============

@app.post("/auth/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user."""
    # Check if username exists
    result = await db.execute(select(User).where(User.username == user_data.username))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password)
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return new_user


@app.post("/auth/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """Login and get access token."""
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/auth/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current authenticated user information."""
    return current_user


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
        "created_at": post.created_at.isoformat(),
        "user_id": str(post.user_id) if post.user_id else None
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
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload a file to ImageKit and create a post record. Requires authentication."""
    # Upload to ImageKit
    upload_result = await upload_to_imagekit(file)
    
    # Create database record with ImageKit URL and user association
    new_post = Post(
        url=upload_result.url,
        file_type=file.content_type or "unknown",
        file_name=file.filename,
        caption=caption,
        user_id=current_user.id
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
        "created_at": new_post.created_at.isoformat(),
        "user_id": str(new_post.user_id)
    }


@app.patch("/items/{item_id}")
async def update_item(
    item_id: str,
    caption: str = Form(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a post's caption. Requires authentication and ownership."""
    try:
        post_uuid = uuid.UUID(item_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    
    result = await db.execute(select(Post).where(Post.id == post_uuid))
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Check ownership
    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to edit this post"
        )
    
    post.caption = caption
    await db.commit()
    await db.refresh(post)
    
    return {
        "id": str(post.id),
        "filename": post.file_name,
        "file_type": post.file_type,
        "url": post.url,
        "caption": post.caption,
        "created_at": post.created_at.isoformat(),
        "user_id": str(post.user_id)
    }


@app.delete("/items/{item_id}")
async def delete_item(
    item_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a specific post by ID. Requires authentication and ownership."""
    try:
        post_uuid = uuid.UUID(item_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")
    
    result = await db.execute(select(Post).where(Post.id == post_uuid))
    post = result.scalar_one_or_none()
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Check ownership
    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this post"
        )
    
    await db.delete(post)
    await db.commit()
    
    return {"message": "Post deleted successfully", "id": str(post_uuid)}
