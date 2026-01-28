from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field


# ============ Car Schemas ============

class CarBase(BaseModel):
    model: str = Field(..., min_length=1, max_length=100)
    number_plate: str = Field(..., min_length=1, max_length=20)
    daily_price: Decimal = Field(..., gt=0)
    deposit: Decimal = Field(..., ge=0)
    image_url: Optional[str] = None
    seats: int = Field(default=5, ge=2, le=12)
    transmission: str = Field(default="automatic")
    fuel_type: str = Field(default="petrol")
    description: Optional[str] = None


class CarCreate(CarBase):
    pass


class CarUpdate(BaseModel):
    model: Optional[str] = Field(None, min_length=1, max_length=100)
    number_plate: Optional[str] = Field(None, min_length=1, max_length=20)
    daily_price: Optional[Decimal] = Field(None, gt=0)
    deposit: Optional[Decimal] = Field(None, ge=0)
    image_url: Optional[str] = None
    seats: Optional[int] = Field(None, ge=2, le=12)
    transmission: Optional[str] = None
    fuel_type: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class CarResponse(CarBase):
    id: UUID
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


# ============ Availability Schemas ============

class AvailabilityBase(BaseModel):
    start_time: datetime
    end_time: datetime
    status: str = "available"


class AvailabilityCreate(AvailabilityBase):
    car_id: UUID


class AvailabilityResponse(AvailabilityBase):
    id: UUID
    car_id: UUID
    
    class Config:
        from_attributes = True


class CarWithAvailability(CarResponse):
    availabilities: List[AvailabilityResponse] = []
    
    class Config:
        from_attributes = True
