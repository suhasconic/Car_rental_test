from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime, timedelta
from decimal import Decimal
from fastapi import APIRouter, HTTPException, status, Query, Depends
from pydantic import BaseModel
from app.core.mock_store import store, Booking, Auction, Bid
from app.api.routes.auth_mock import get_current_user, User
from app.core.config import settings

router = APIRouter(prefix="/bookings", tags=["Bookings"])


# ============ Schemas ============

class BookingCreate(BaseModel):
    car_id: str
    start_time: datetime
    end_time: datetime
    offer_price: float


class BookingResponse(BaseModel):
    id: str
    user_id: str
    car_id: str
    start_time: datetime
    end_time: datetime
    offer_price: float
    status: str
    created_at: datetime


def booking_to_response(booking: Booking) -> dict:
    car = store.get_car_by_id(booking.car_id)
    user = store.get_user_by_id(booking.user_id)
    
    return {
        "id": str(booking.id),
        "user_id": str(booking.user_id),
        "car_id": str(booking.car_id),
        "start_time": booking.start_time.isoformat(),
        "end_time": booking.end_time.isoformat(),
        "offer_price": float(booking.offer_price),
        "status": booking.status,
        "created_at": booking.created_at.isoformat(),
        "updated_at": booking.updated_at.isoformat(),
        "car": {
            "id": str(car.id),
            "model": car.model,
            "number_plate": car.number_plate,
            "daily_price": float(car.daily_price),
            "deposit": float(car.deposit),
            "image_url": car.image_url,
            "seats": car.seats,
            "transmission": car.transmission,
            "fuel_type": car.fuel_type,
        } if car else None,
        "user": {
            "id": str(user.id),
            "name": user.name,
            "total_rides": user.total_rides,
            "avg_rating": float(user.avg_rating),
            "trust_score": float(user.trust_score),
            "is_blocked": user.is_blocked,
        } if user else None,
    }


# ============ Routes ============

@router.post("/request")
def request_booking(
    booking_data: BookingCreate,
    current_user: User = Depends(get_current_user)
):
    """Request a booking for a car"""
    if booking_data.start_time >= booking_data.end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End time must be after start time"
        )
    
    # Check if user should be auto-rejected
    if float(current_user.trust_score) < settings.AUTO_REJECT_THRESHOLD or current_user.is_blocked:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Your account is not eligible for bookings at this time."
        )
    
    # Check if car exists
    try:
        car_id = UUID(booking_data.car_id)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid car ID")
    
    car = store.get_car_by_id(car_id)
    if not car or not car.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Car not found or not available")
    
    # Check for confirmed bookings (hard block)
    for b in store.bookings.values():
        if b.car_id == car_id and b.status == "confirmed":
            if b.start_time < booking_data.end_time and b.end_time > booking_data.start_time:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Car is already booked for this time period."
                )
    
    # Create booking
    booking = Booking(
        id=uuid4(),
        user_id=current_user.id,
        car_id=car_id,
        start_time=booking_data.start_time,
        end_time=booking_data.end_time,
        offer_price=Decimal(str(booking_data.offer_price)),
        status="pending"
    )
    store.create_booking(booking)
    
    # Check for conflicts
    conflicts = store.get_conflicting_bookings(
        car_id, booking_data.start_time, booking_data.end_time, exclude_id=booking.id
    )
    
    if conflicts:
        # Create or get auction
        auction = None
        for a in store.auctions.values():
            if a.car_id == car_id and a.status == "active":
                if a.start_time < booking_data.end_time and a.end_time > booking_data.start_time:
                    auction = a
                    break
        
        if not auction:
            auction = Auction(
                id=uuid4(),
                car_id=car_id,
                start_time=booking_data.start_time,
                end_time=booking_data.end_time,
                auction_end=datetime.utcnow() + timedelta(hours=settings.AUCTION_DURATION_HOURS)
            )
            store.create_auction(auction)
        
        # Add all conflicts to auction
        for conflict in conflicts:
            existing_bid = store.get_bid_by_user_auction(conflict.user_id, auction.id)
            if not existing_bid:
                conflict_user = store.get_user_by_id(conflict.user_id)
                bid = Bid(
                    id=uuid4(),
                    auction_id=auction.id,
                    user_id=conflict.user_id,
                    booking_id=conflict.id,
                    offer_price=conflict.offer_price,
                    trust_score_snapshot=conflict_user.trust_score if conflict_user else Decimal("0")
                )
                store.create_bid(bid)
                conflict.status = "competing"
        
        # Add current booking to auction
        existing_bid = store.get_bid_by_user_auction(current_user.id, auction.id)
        if not existing_bid:
            bid = Bid(
                id=uuid4(),
                auction_id=auction.id,
                user_id=current_user.id,
                booking_id=booking.id,
                offer_price=booking.offer_price,
                trust_score_snapshot=current_user.trust_score
            )
            store.create_bid(bid)
        
        booking.status = "competing"
    
    return booking_to_response(booking)


@router.get("/my")
def get_my_bookings(
    status_filter: Optional[str] = Query(None, alias="status"),
    current_user: User = Depends(get_current_user)
):
    """Get all bookings for the current user"""
    bookings = store.get_bookings_by_user(current_user.id, status_filter)
    return [booking_to_response(b) for b in bookings]


@router.get("/{booking_id}")
def get_booking(
    booking_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get booking details"""
    try:
        booking = store.get_booking_by_id(UUID(booking_id))
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    
    if booking.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    return booking_to_response(booking)


@router.post("/{booking_id}/cancel")
def cancel_booking(
    booking_id: str,
    current_user: User = Depends(get_current_user)
):
    """Cancel a booking"""
    try:
        booking = store.get_booking_by_id(UUID(booking_id))
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    
    if booking.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only cancel your own bookings")
    
    if booking.status not in ["pending", "competing", "confirmed"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This booking cannot be cancelled")
    
    # Apply late cancellation penalty
    # Make sure both datetimes are offset-naive for comparison
    start_time = booking.start_time.replace(tzinfo=None) if booking.start_time.tzinfo else booking.start_time
    hours_until_start = (start_time - datetime.utcnow()).total_seconds() / 3600
    if hours_until_start < 24 and booking.status == "confirmed":
        current_score = float(current_user.trust_score)
        current_user.trust_score = Decimal(str(max(0, current_score - settings.LATE_CANCEL_PENALTY)))
    
    booking.status = "cancelled"
    booking.updated_at = datetime.utcnow()
    
    return booking_to_response(booking)
