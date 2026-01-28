from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel
from app.core.mock_store import store, Car

router = APIRouter(prefix="/cars", tags=["Cars"])


# ============ Schemas ============

class CarResponse(BaseModel):
    id: str
    model: str
    number_plate: str
    daily_price: float
    deposit: float
    image_url: Optional[str]
    seats: int
    transmission: str
    fuel_type: str
    description: Optional[str]
    is_active: bool


def car_to_response(car: Car) -> dict:
    return {
        "id": str(car.id),
        "model": car.model,
        "number_plate": car.number_plate,
        "daily_price": float(car.daily_price),
        "deposit": float(car.deposit),
        "image_url": car.image_url,
        "seats": car.seats,
        "transmission": car.transmission,
        "fuel_type": car.fuel_type,
        "description": car.description,
        "is_active": car.is_active,
    }


# ============ Routes ============

@router.get("", response_model=List[CarResponse])
def list_cars(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    transmission: Optional[str] = None,
    fuel_type: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
):
    """List all active cars with optional filters"""
    cars = store.get_all_cars(active_only=True)
    
    # Apply filters
    if transmission:
        cars = [c for c in cars if c.transmission == transmission]
    if fuel_type:
        cars = [c for c in cars if c.fuel_type == fuel_type]
    if min_price is not None:
        cars = [c for c in cars if float(c.daily_price) >= min_price]
    if max_price is not None:
        cars = [c for c in cars if float(c.daily_price) <= max_price]
    
    # Pagination
    cars = cars[skip:skip + limit]
    
    return [car_to_response(car) for car in cars]


@router.get("/{car_id}", response_model=CarResponse)
def get_car(car_id: str):
    """Get car details"""
    try:
        car = store.get_car_by_id(UUID(car_id))
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Car not found")
    
    if not car:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Car not found")
    
    return car_to_response(car)


@router.get("/{car_id}/availability")
def get_car_availability(car_id: str):
    """Get availability for a car (simplified - all cars available)"""
    try:
        car = store.get_car_by_id(UUID(car_id))
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Car not found")
    
    if not car:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Car not found")
    
    # Return simplified availability (always available for now)
    return []
