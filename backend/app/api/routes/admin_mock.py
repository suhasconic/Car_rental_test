from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime
from decimal import Decimal
from fastapi import APIRouter, HTTPException, status, Query, Depends
from pydantic import BaseModel
from app.core.mock_store import store, Car, Ride, Rating
from app.api.routes.auth_mock import get_current_user, get_current_admin, user_to_response, User
from app.core.config import settings

router = APIRouter(prefix="/admin", tags=["Admin"])


# ============ Schemas ============

class CarCreate(BaseModel):
    model: str
    number_plate: str
    daily_price: float
    deposit: float
    image_url: Optional[str] = None
    seats: int = 5
    transmission: str = "automatic"
    fuel_type: str = "petrol"
    description: Optional[str] = None


class CarUpdate(BaseModel):
    model: Optional[str] = None
    number_plate: Optional[str] = None
    daily_price: Optional[float] = None
    deposit: Optional[float] = None
    image_url: Optional[str] = None
    seats: Optional[int] = None
    transmission: Optional[str] = None
    fuel_type: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class RatingCreate(BaseModel):
    driving_rating: int
    damage_flag: bool = False
    rash_flag: bool = False
    notes: Optional[str] = None


# ============ Helpers ============

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


def booking_with_details(booking):
    car = store.get_car_by_id(booking.car_id)
    user = store.get_user_by_id(booking.user_id)
    ride = store.get_ride_by_booking(booking.id)
    rating = store.get_rating_by_ride(ride.id) if ride else None
    
    return {
        "id": str(booking.id),
        "user_id": str(booking.user_id),
        "car_id": str(booking.car_id),
        "start_time": booking.start_time.isoformat(),
        "end_time": booking.end_time.isoformat(),
        "offer_price": float(booking.offer_price),
        "status": booking.status,
        "created_at": booking.created_at.isoformat(),
        "car": car_to_response(car) if car else None,
        "user": user_to_response(user) if user else None,
        "ride": {
            "id": str(ride.id),
            "status": ride.status,
            "started_at": ride.started_at.isoformat(),
            "ended_at": ride.ended_at.isoformat() if ride.ended_at else None,
            "rating": {
                "id": str(rating.id),
                "driving_rating": rating.driving_rating,
                "damage_flag": rating.damage_flag,
                "rash_flag": rating.rash_flag,
                "notes": rating.notes,
            } if rating else None
        } if ride else None
    }


# ============ Dashboard ============

@router.get("/dashboard")
def get_dashboard(admin: User = Depends(get_current_admin)):
    """Get admin dashboard statistics"""
    users = [u for u in store.users.values() if u.role == "user"]
    
    return {
        "users": {
            "total": len(users),
            "blocked": len([u for u in users if u.is_blocked]),
            "active": len([u for u in users if not u.is_blocked])
        },
        "cars": {
            "total": len(store.cars),
            "active": len([c for c in store.cars.values() if c.is_active]),
            "inactive": len([c for c in store.cars.values() if not c.is_active])
        },
        "bookings": {
            "pending": len([b for b in store.bookings.values() if b.status == "pending"]),
            "active": len([b for b in store.bookings.values() if b.status == "confirmed"])
        },
        "auctions": {
            "active": len([a for a in store.auctions.values() if a.status == "active"])
        },
        "rides": {
            "active": len([r for r in store.rides.values() if r.status == "active"])
        }
    }


# ============ Car Management ============

@router.post("/cars")
def add_car(car_data: CarCreate, admin: User = Depends(get_current_admin)):
    """Add a new car to the fleet"""
    # Check for duplicate number plate
    for car in store.cars.values():
        if car.number_plate == car_data.number_plate:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Car with this number plate already exists"
            )
    
    car = Car(
        id=uuid4(),
        model=car_data.model,
        number_plate=car_data.number_plate,
        daily_price=Decimal(str(car_data.daily_price)),
        deposit=Decimal(str(car_data.deposit)),
        image_url=car_data.image_url,
        seats=car_data.seats,
        transmission=car_data.transmission,
        fuel_type=car_data.fuel_type,
        description=car_data.description,
    )
    store.create_car(car)
    
    return car_to_response(car)


@router.put("/cars/{car_id}")
def update_car(car_id: str, car_data: CarUpdate, admin: User = Depends(get_current_admin)):
    """Update car details"""
    try:
        car = store.get_car_by_id(UUID(car_id))
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Car not found")
    
    if not car:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Car not found")
    
    update_data = car_data.dict(exclude_unset=True)
    if "daily_price" in update_data:
        update_data["daily_price"] = Decimal(str(update_data["daily_price"]))
    if "deposit" in update_data:
        update_data["deposit"] = Decimal(str(update_data["deposit"]))
    
    store.update_car(UUID(car_id), update_data)
    
    return car_to_response(car)


@router.delete("/cars/{car_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_car(car_id: str, admin: User = Depends(get_current_admin)):
    """Remove a car from the fleet"""
    try:
        car = store.get_car_by_id(UUID(car_id))
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Car not found")
    
    if not car:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Car not found")
    
    # Check for active bookings
    for booking in store.bookings.values():
        if booking.car_id == UUID(car_id) and booking.status in ["confirmed", "pending"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete car with active bookings"
            )
    
    store.delete_car(UUID(car_id))


# ============ Booking Management ============

@router.get("/bookings")
def list_all_bookings(
    status_filter: Optional[str] = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    admin: User = Depends(get_current_admin)
):
    """List all bookings (admin view)"""
    bookings = store.get_all_bookings(status_filter)
    bookings = bookings[skip:skip + limit]
    return [booking_with_details(b) for b in bookings]


@router.post("/bookings/{booking_id}/approve")
def approve_booking(booking_id: str, admin: User = Depends(get_current_admin)):
    """Approve a pending booking"""
    try:
        booking = store.get_booking_by_id(UUID(booking_id))
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    
    if booking.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot approve booking with status: {booking.status}"
        )
    
    booking.status = "confirmed"
    booking.updated_at = datetime.utcnow()
    
    return booking_with_details(booking)


@router.post("/bookings/{booking_id}/reject")
def reject_booking(booking_id: str, admin: User = Depends(get_current_admin)):
    """Reject a pending booking"""
    try:
        booking = store.get_booking_by_id(UUID(booking_id))
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    
    if booking.status not in ["pending", "competing"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot reject booking with status: {booking.status}"
        )
    
    booking.status = "rejected"
    booking.updated_at = datetime.utcnow()
    
    return booking_with_details(booking)


# ============ Ride Management ============

@router.post("/bookings/{booking_id}/start-ride")
def start_ride(booking_id: str, admin: User = Depends(get_current_admin)):
    """Start a ride for a confirmed booking"""
    try:
        booking = store.get_booking_by_id(UUID(booking_id))
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    
    if not booking:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Booking not found")
    
    if booking.status != "confirmed":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only confirmed bookings can start rides")
    
    existing_ride = store.get_ride_by_booking(booking.id)
    if existing_ride:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ride already started")
    
    ride = Ride(id=uuid4(), booking_id=booking.id)
    store.create_ride(ride)
    
    return {"message": "Ride started", "ride_id": str(ride.id)}


@router.post("/rides/{ride_id}/complete")
def complete_ride(ride_id: str, admin: User = Depends(get_current_admin)):
    """Complete an active ride"""
    try:
        ride = store.get_ride_by_id(UUID(ride_id))
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ride not found")
    
    if not ride:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ride not found")
    
    if ride.status != "active":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only active rides can be completed")
    
    ride.status = "completed"
    ride.ended_at = datetime.utcnow()
    
    # Update booking status
    booking = store.get_booking_by_id(ride.booking_id)
    if booking:
        booking.status = "completed"
    
    return {"message": "Ride completed", "ride_id": str(ride.id)}


@router.post("/rides/{ride_id}/rate")
def rate_ride(ride_id: str, rating_data: RatingCreate, admin: User = Depends(get_current_admin)):
    """Rate a completed ride and update user trust score"""
    try:
        ride = store.get_ride_by_id(UUID(ride_id))
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ride not found")
    
    if not ride:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ride not found")
    
    if ride.status not in ["completed", "damaged"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only completed or damaged rides can be rated")
    
    existing_rating = store.get_rating_by_ride(ride.id)
    if existing_rating:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ride already rated")
    
    # Create rating
    rating = Rating(
        id=uuid4(),
        ride_id=ride.id,
        driving_rating=rating_data.driving_rating,
        damage_flag=rating_data.damage_flag,
        rash_flag=rating_data.rash_flag,
        notes=rating_data.notes
    )
    store.create_rating(rating)
    
    # Update ride status if damaged
    if rating_data.damage_flag:
        ride.status = "damaged"
    
    # Update user trust score
    booking = store.get_booking_by_id(ride.booking_id)
    if booking:
        user = store.get_user_by_id(booking.user_id)
        if user:
            # Increment ride count
            user.total_rides += 1
            
            # Update average rating
            old_avg = float(user.avg_rating)
            new_avg = ((old_avg * (user.total_rides - 1)) + rating_data.driving_rating) / user.total_rides
            user.avg_rating = Decimal(str(round(new_avg, 2)))
            
            # Update incident counts
            if rating_data.damage_flag:
                user.damage_count += 1
            if rating_data.rash_flag:
                user.rash_count += 1
            
            # Recalculate trust score
            user.trust_score = user.calculate_trust_score()
            
            # Auto-block check
            if float(user.trust_score) < settings.AUTO_BLOCK_THRESHOLD:
                user.is_blocked = True
    
    return {
        "id": str(rating.id),
        "ride_id": str(rating.ride_id),
        "driving_rating": rating.driving_rating,
        "damage_flag": rating.damage_flag,
        "rash_flag": rating.rash_flag,
        "notes": rating.notes
    }


# ============ User Management ============

@router.get("/users")
def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    blocked_only: bool = Query(False),
    admin: User = Depends(get_current_admin)
):
    """List all users (admin view)"""
    users = store.get_all_users(role="user", blocked_only=blocked_only)
    users = users[skip:skip + limit]
    return [user_to_response(u) for u in users]


@router.get("/users/leaderboard")
def get_trust_leaderboard(
    limit: int = Query(10, ge=1, le=50),
    admin: User = Depends(get_current_admin)
):
    """Get top users by trust score"""
    users = [u for u in store.users.values() if u.role == "user" and not u.is_blocked]
    users = sorted(users, key=lambda u: float(u.trust_score), reverse=True)[:limit]
    return [user_to_response(u) for u in users]


@router.post("/users/{user_id}/block")
def block_user(user_id: str, admin: User = Depends(get_current_admin)):
    """Block a user"""
    try:
        user = store.get_user_by_id(UUID(user_id))
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if user.role == "admin":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot block admin users")
    
    user.is_blocked = True
    
    return {"message": "User blocked", "user_id": user_id}


@router.post("/users/{user_id}/unblock")
def unblock_user(user_id: str, admin: User = Depends(get_current_admin)):
    """Unblock a user"""
    try:
        user = store.get_user_by_id(UUID(user_id))
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    user.is_blocked = False
    
    return {"message": "User unblocked", "user_id": user_id}


# ============ Auction Management ============

@router.get("/auctions")
def list_all_auctions(
    status_filter: Optional[str] = Query(None, alias="status"),
    admin: User = Depends(get_current_admin)
):
    """List all auctions (admin view)"""
    from app.api.routes.auctions_mock import auction_to_response
    
    auctions = store.get_all_auctions(status_filter)
    return [auction_to_response(a) for a in auctions]


@router.post("/auctions/{auction_id}/close")
def close_auction(auction_id: str, admin: User = Depends(get_current_admin)):
    """Manually close an auction and determine winner"""
    try:
        auction = store.get_auction_by_id(UUID(auction_id))
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Auction not found")
    
    if not auction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Auction not found")
    
    if auction.status != "active":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Auction is already closed")
    
    bids = store.get_auction_bids(auction.id)
    
    if not bids:
        auction.status = "closed"
        return {"message": "Auction closed with no bids", "winner_id": None}
    
    # Calculate final scores
    max_trust = max(float(b.trust_score_snapshot) for b in bids) or 1
    max_rides = max(store.get_user_by_id(b.user_id).total_rides for b in bids) or 1
    max_price = max(float(b.offer_price) for b in bids) or 1
    
    for bid in bids:
        user = store.get_user_by_id(bid.user_id)
        normalized_trust = float(bid.trust_score_snapshot) / max_trust
        normalized_rides = (user.total_rides if user else 0) / max_rides
        normalized_price = float(bid.offer_price) / max_price
        
        bid.final_score = Decimal(str(round(
            0.5 * normalized_trust + 0.3 * normalized_rides + 0.2 * normalized_price, 4
        )))
    
    # Determine winner
    eligible_bids = [b for b in bids if float(b.trust_score_snapshot) >= settings.TRUST_THRESHOLD]
    
    if eligible_bids:
        winner_bid = max(eligible_bids, key=lambda b: float(b.final_score or 0))
    else:
        winner_bid = max(bids, key=lambda b: float(b.offer_price))
    
    # Update auction
    auction.status = "closed"
    auction.winner_id = winner_bid.user_id
    auction.auction_end = datetime.utcnow()
    
    # Update bookings
    for bid in bids:
        booking = store.get_booking_by_id(bid.booking_id)
        if booking:
            if bid.id == winner_bid.id:
                booking.status = "confirmed"
            else:
                booking.status = "rejected"
    
    return {
        "message": "Auction closed",
        "winner_id": str(auction.winner_id),
        "winning_booking_id": str(winner_bid.booking_id)
    }
