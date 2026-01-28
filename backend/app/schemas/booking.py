from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field
from app.schemas.user import UserPublic
from app.schemas.car import CarResponse


# ============ Booking Schemas ============

class BookingCreate(BaseModel):
    car_id: UUID
    start_time: datetime
    end_time: datetime
    offer_price: Decimal = Field(..., gt=0)


class BookingResponse(BaseModel):
    id: UUID
    user_id: UUID
    car_id: UUID
    start_time: datetime
    end_time: datetime
    offer_price: Decimal
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class BookingWithDetails(BookingResponse):
    user: Optional[UserPublic] = None
    car: Optional[CarResponse] = None
    
    class Config:
        from_attributes = True


# ============ Ride Schemas ============

class RideResponse(BaseModel):
    id: UUID
    booking_id: UUID
    status: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class RideWithBooking(RideResponse):
    booking: Optional[BookingWithDetails] = None
    
    class Config:
        from_attributes = True


# ============ Rating Schemas ============

class RatingCreate(BaseModel):
    driving_rating: int = Field(..., ge=1, le=5)
    damage_flag: bool = False
    rash_flag: bool = False
    notes: Optional[str] = None


class RatingResponse(BaseModel):
    id: UUID
    ride_id: UUID
    driving_rating: int
    damage_flag: bool
    rash_flag: bool
    notes: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True
