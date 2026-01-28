from typing import List, Optional
from uuid import UUID
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import (
    User, Car, Booking, Auction, Ride, Rating,
    BookingStatus, AuctionStatus, RideStatus, Availability, AvailabilityStatus
)
from app.schemas import (
    CarCreate, CarUpdate, CarResponse,
    BookingResponse, BookingWithDetails,
    RatingCreate, RatingResponse,
    UserResponse, UserPublic,
    AuctionWithDetails
)
from app.api.deps import get_current_admin
from app.services import trust_engine, auction_engine

router = APIRouter(prefix="/admin", tags=["Admin"])


# ============ Dashboard ============

@router.get("/dashboard")
def get_dashboard(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get admin dashboard statistics"""
    total_users = db.query(User).filter(User.role == "user").count()
    blocked_users = db.query(User).filter(User.is_blocked == True).count()
    total_cars = db.query(Car).count()
    active_cars = db.query(Car).filter(Car.is_active == True).count()
    
    pending_bookings = db.query(Booking).filter(
        Booking.status == BookingStatus.PENDING.value
    ).count()
    active_bookings = db.query(Booking).filter(
        Booking.status == BookingStatus.CONFIRMED.value
    ).count()
    
    active_auctions = db.query(Auction).filter(
        Auction.status == AuctionStatus.ACTIVE.value
    ).count()
    
    active_rides = db.query(Ride).filter(
        Ride.status == RideStatus.ACTIVE.value
    ).count()
    
    return {
        "users": {
            "total": total_users,
            "blocked": blocked_users,
            "active": total_users - blocked_users
        },
        "cars": {
            "total": total_cars,
            "active": active_cars,
            "inactive": total_cars - active_cars
        },
        "bookings": {
            "pending": pending_bookings,
            "active": active_bookings
        },
        "auctions": {
            "active": active_auctions
        },
        "rides": {
            "active": active_rides
        }
    }


# ============ Car Management ============

@router.post("/cars", response_model=CarResponse, status_code=status.HTTP_201_CREATED)
def add_car(
    car_data: CarCreate,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Add a new car to the fleet"""
    # Check for duplicate number plate
    existing = db.query(Car).filter(Car.number_plate == car_data.number_plate).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Car with this number plate already exists"
        )
    
    car = Car(**car_data.model_dump())
    db.add(car)
    db.commit()
    db.refresh(car)
    return car


@router.put("/cars/{car_id}", response_model=CarResponse)
def update_car(
    car_id: UUID,
    car_data: CarUpdate,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update car details"""
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Car not found"
        )
    
    update_data = car_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(car, field, value)
    
    car.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(car)
    return car


@router.delete("/cars/{car_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_car(
    car_id: UUID,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Remove a car from the fleet"""
    car = db.query(Car).filter(Car.id == car_id).first()
    if not car:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Car not found"
        )
    
    # Check for active bookings
    active_booking = db.query(Booking).filter(
        Booking.car_id == car_id,
        Booking.status.in_([BookingStatus.CONFIRMED.value, BookingStatus.PENDING.value])
    ).first()
    
    if active_booking:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete car with active bookings"
        )
    
    db.delete(car)
    db.commit()


# ============ Booking Management ============

@router.get("/bookings", response_model=List[BookingWithDetails])
def list_all_bookings(
    status_filter: Optional[str] = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """List all bookings (admin view)"""
    query = db.query(Booking)
    
    if status_filter:
        query = query.filter(Booking.status == status_filter)
    
    return query.order_by(Booking.created_at.desc()).offset(skip).limit(limit).all()


@router.post("/bookings/{booking_id}/approve", response_model=BookingResponse)
def approve_booking(
    booking_id: UUID,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Approve a pending booking"""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    if booking.status != BookingStatus.PENDING.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot approve booking with status: {booking.status}"
        )
    
    booking.status = BookingStatus.CONFIRMED.value
    booking.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(booking)
    return booking


@router.post("/bookings/{booking_id}/reject", response_model=BookingResponse)
def reject_booking(
    booking_id: UUID,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Reject a pending booking"""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    if booking.status not in [BookingStatus.PENDING.value, BookingStatus.COMPETING.value]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot reject booking with status: {booking.status}"
        )
    
    booking.status = BookingStatus.REJECTED.value
    booking.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(booking)
    return booking


# ============ Ride Management ============

@router.post("/bookings/{booking_id}/start-ride")
def start_ride(
    booking_id: UUID,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Start a ride for a confirmed booking"""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    if booking.status != BookingStatus.CONFIRMED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only confirmed bookings can start rides"
        )
    
    if booking.ride:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ride already started"
        )
    
    ride = Ride(
        booking_id=booking_id,
        status=RideStatus.ACTIVE.value,
        started_at=datetime.utcnow()
    )
    db.add(ride)
    db.commit()
    db.refresh(ride)
    
    return {"message": "Ride started", "ride_id": str(ride.id)}


@router.post("/rides/{ride_id}/complete")
def complete_ride(
    ride_id: UUID,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Complete an active ride"""
    ride = db.query(Ride).filter(Ride.id == ride_id).first()
    if not ride:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ride not found"
        )
    
    if ride.status != RideStatus.ACTIVE.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only active rides can be completed"
        )
    
    ride.status = RideStatus.COMPLETED.value
    ride.ended_at = datetime.utcnow()
    
    # Update booking status
    ride.booking.status = BookingStatus.COMPLETED.value
    
    db.commit()
    db.refresh(ride)
    
    return {"message": "Ride completed", "ride_id": str(ride.id)}


@router.post("/rides/{ride_id}/rate", response_model=RatingResponse)
def rate_ride(
    ride_id: UUID,
    rating_data: RatingCreate,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Rate a completed ride and update user trust score"""
    ride = db.query(Ride).filter(Ride.id == ride_id).first()
    if not ride:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ride not found"
        )
    
    if ride.status not in [RideStatus.COMPLETED.value, RideStatus.DAMAGED.value]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only completed or damaged rides can be rated"
        )
    
    if ride.rating:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ride already rated"
        )
    
    # Create rating
    rating = Rating(
        ride_id=ride_id,
        driving_rating=rating_data.driving_rating,
        damage_flag=rating_data.damage_flag,
        rash_flag=rating_data.rash_flag,
        notes=rating_data.notes
    )
    db.add(rating)
    
    # Update ride status if damaged
    if rating_data.damage_flag:
        ride.status = RideStatus.DAMAGED.value
    
    db.commit()
    db.refresh(rating)
    
    # Update user trust score
    user = ride.booking.user
    trust_engine.update_after_rating(db, user, rating)
    
    return rating


# ============ User Management ============

@router.get("/users", response_model=List[UserResponse])
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    blocked_only: bool = Query(False),
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """List all users (admin view)"""
    query = db.query(User).filter(User.role == "user")
    
    if blocked_only:
        query = query.filter(User.is_blocked == True)
    
    return query.order_by(User.trust_score.desc()).offset(skip).limit(limit).all()


@router.get("/users/leaderboard", response_model=List[UserPublic])
def get_trust_leaderboard(
    limit: int = Query(10, ge=1, le=50),
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get top users by trust score"""
    return (
        db.query(User)
        .filter(User.role == "user", User.is_blocked == False)
        .order_by(User.trust_score.desc())
        .limit(limit)
        .all()
    )


@router.post("/users/{user_id}/block")
def block_user(
    user_id: UUID,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Block a user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.role == "admin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot block admin users"
        )
    
    user.is_blocked = True
    db.commit()
    
    return {"message": "User blocked", "user_id": str(user_id)}


@router.post("/users/{user_id}/unblock")
def unblock_user(
    user_id: UUID,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Unblock a user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.is_blocked = False
    db.commit()
    
    return {"message": "User unblocked", "user_id": str(user_id)}


# ============ Auction Management ============

@router.get("/auctions", response_model=List[AuctionWithDetails])
def list_all_auctions(
    status_filter: Optional[str] = Query(None, alias="status"),
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """List all auctions (admin view)"""
    query = db.query(Auction)
    
    if status_filter:
        query = query.filter(Auction.status == status_filter)
    
    auctions = query.order_by(Auction.created_at.desc()).all()
    
    return [
        AuctionWithDetails(
            id=a.id,
            car_id=a.car_id,
            start_time=a.start_time,
            end_time=a.end_time,
            auction_start=a.auction_start,
            auction_end=a.auction_end,
            status=a.status,
            winner_id=a.winner_id,
            created_at=a.created_at,
            car=a.car,
            winner=a.winner,
            bids=a.bids,
            bid_count=len(a.bids)
        )
        for a in auctions
    ]


@router.post("/auctions/{auction_id}/close")
def close_auction(
    auction_id: UUID,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Manually close an auction and determine winner"""
    auction = db.query(Auction).filter(Auction.id == auction_id).first()
    if not auction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Auction not found"
        )
    
    if auction.status != AuctionStatus.ACTIVE.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Auction is already closed"
        )
    
    winning_booking = auction_engine.close_auction(db, auction)
    
    return {
        "message": "Auction closed",
        "winner_id": str(auction.winner_id) if auction.winner_id else None,
        "winning_booking_id": str(winning_booking.id) if winning_booking else None
    }
