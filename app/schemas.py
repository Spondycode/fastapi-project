"""Pydantic schemas for request/response models."""

from pydantic import BaseModel, EmailStr, Field, field_serializer
from datetime import datetime
from typing import Optional
from uuid import UUID


class UserCreate(BaseModel):
    """Schema for creating a new user."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserResponse(BaseModel):
    """Schema for user response (without password)."""
    id: UUID
    username: str
    email: str
    is_active: bool
    created_at: datetime
    
    @field_serializer('id')
    def serialize_id(self, value: UUID, _info) -> str:
        """Convert UUID to string for JSON serialization."""
        return str(value)
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for token payload data."""
    username: Optional[str] = None
