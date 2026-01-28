from datetime import timedelta
from uuid import uuid4
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr
from typing import Optional
from app.core.mock_store import store, User
from app.core.security import verify_password, get_password_hash, create_access_token, decode_access_token
from app.core.config import settings
from decimal import Decimal

router = APIRouter(prefix="/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# ============ Schemas ============

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    phone: Optional[str]
    role: str
    total_rides: int
    avg_rating: float
    damage_count: int
    rash_count: int
    trust_score: float
    is_blocked: bool


# ============ Dependencies ============

def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    from uuid import UUID
    user = store.get_user_by_id(UUID(user_id))
    if user is None:
        raise credentials_exception
    
    if user.is_blocked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been blocked"
        )
    
    return user


def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def user_to_response(user: User) -> dict:
    return {
        "id": str(user.id),
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "role": user.role,
        "total_rides": user.total_rides,
        "avg_rating": float(user.avg_rating),
        "damage_count": user.damage_count,
        "rash_count": user.rash_count,
        "trust_score": float(user.trust_score),
        "is_blocked": user.is_blocked,
    }


# ============ Routes ============

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(user_data: UserCreate):
    """Register a new user"""
    # Check if email already exists
    existing_user = store.get_user_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user = User(
        id=uuid4(),
        name=user_data.name,
        email=user_data.email,
        phone=user_data.phone,
        password_hash=get_password_hash(user_data.password),
        role="user",
        trust_score=Decimal("50.00")
    )
    store.create_user(user)
    
    return user_to_response(user)


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login and get access token"""
    user = store.get_user_by_email(form_data.username)
    
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if user.is_blocked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been blocked"
        )
    
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role}
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login/json", response_model=Token)
def login_json(credentials: UserLogin):
    """Login with JSON body"""
    user = store.get_user_by_email(credentials.email)
    
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if user.is_blocked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been blocked"
        )
    
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role}
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return user_to_response(current_user)
