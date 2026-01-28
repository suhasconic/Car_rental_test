from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import Car, Availability, AvailabilityStatus
from app.schemas import CarResponse, CarWithAvailability, AvailabilityResponse
from app.api.deps import get_optional_user

router = APIRouter(prefix="/cars", tags=["Cars"])


@router.get("", response_model=List[CarResponse])
def list_cars(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    transmission: Optional[str] = None,
    fuel_type: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    db: Session = Depends(get_db)
):
    """List all active cars with optional filters"""
    query = db.query(Car).filter(Car.is_active == True)
    
    if transmission:
        query = query.filter(Car.transmission == transmission)
    if fuel_type:
        query = query.filter(Car.fuel_type == fuel_type)
    if min_price is not None:
        query = query.filter(Car.daily_price >= min_price)
    if max_price is not None:
        query = query.filter(Car.daily_price <= max_price)
    
    return query.offset(skip).limit(limit).all()


@router.get("/{car_id}", response_model=CarWithAvailability)
def get_car(car_id: UUID, db: Session = Depends(get_db)):
    """Get car details with availability"""
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Car not found"
        )
    return car


@router.get("/{car_id}/availability", response_model=List[AvailabilityResponse])
def get_car_availability(
    car_id: UUID,
    status_filter: Optional[str] = Query(None, alias="status"),
    db: Session = Depends(get_db)
):
    """Get availability slots for a car"""
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Car not found"
        )
    
    query = db.query(Availability).filter(Availability.car_id == car_id)
    
    if status_filter:
        query = query.filter(Availability.status == status_filter)
    
    return query.order_by(Availability.start_time).all()
