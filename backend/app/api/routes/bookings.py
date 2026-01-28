from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import User, Booking, BookingStatus
from app.schemas import BookingCreate, BookingResponse, BookingWithDetails
from app.api.deps import get_current_active_user
from app.services import booking_engine

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post("/request", response_model=BookingResponse)
def request_booking(
    booking_data: BookingCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Request a booking for a car.
    
    If there are conflicting bookings, an auction will be triggered.
    """
    if booking_data.start_time >= booking_data.end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End time must be after start time"
        )
    
    try:
        booking, warning = booking_engine.create_booking_request(
            db=db,
            user=current_user,
            car_id=booking_data.car_id,
            start_time=booking_data.start_time,
            end_time=booking_data.end_time,
            offer_price=booking_data.offer_price
        )
        
        # Add warning to response headers if present
        response_booking = BookingResponse.model_validate(booking)
        return response_booking
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/my", response_model=List[BookingWithDetails])
def get_my_bookings(
    status_filter: Optional[str] = Query(None, alias="status"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all bookings for the current user"""
    query = db.query(Booking).filter(Booking.user_id == current_user.id)
    
    if status_filter:
        query = query.filter(Booking.status == status_filter)
    
    bookings = query.order_by(Booking.created_at.desc()).all()
    return bookings


@router.get("/{booking_id}", response_model=BookingWithDetails)
def get_booking(
    booking_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get booking details"""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    # Users can only see their own bookings (unless admin)
    if booking.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return booking


@router.post("/{booking_id}/cancel", response_model=BookingResponse)
def cancel_booking(
    booking_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Cancel a booking (may incur trust penalty for late cancellation)"""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    if booking.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only cancel your own bookings"
        )
    
    try:
        booking = booking_engine.cancel_booking(db, booking, current_user)
        return booking
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
