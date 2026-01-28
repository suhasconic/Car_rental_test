from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field, validator


# ============ Auth Schemas ============

class UserCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[str] = None


# ============ User Schemas ============

class UserBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None


class UserResponse(UserBase):
    id: UUID
    role: str
    total_rides: int
    avg_rating: Decimal
    damage_count: int
    rash_count: int
    trust_score: Decimal
    is_blocked: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserPublic(BaseModel):
    """Public user info (for other users to see)"""
    id: UUID
    name: str
    total_rides: int
    avg_rating: Decimal
    trust_score: Decimal
    is_blocked: bool
    
    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
