from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.models import Booking, Availability, User, Car, BookingStatus, AvailabilityStatus
from app.services.trust_engine import trust_engine
from app.services.auction_engine import auction_engine
from app.core.config import settings


class BookingEngine:
    """
    Booking Engine
    
    Handles:
    - Creating booking requests
    - Checking availability
    - Triggering auctions on conflicts
    - Cancellation handling
    """
    
    @staticmethod
    def check_availability(
        db: Session,
        car_id: UUID,
        start_time: datetime,
        end_time: datetime
    ) -> bool:
        """Check if car is available for the requested time slot"""
        # Check if car exists and is active
        car = db.query(Car).filter(Car.id == car_id, Car.is_active == True).first()
        if not car:
            return False
        
        # Check for existing confirmed bookings
        conflicting_booking = (
            db.query(Booking)
            .filter(
                Booking.car_id == car_id,
                Booking.status == BookingStatus.CONFIRMED.value,
                Booking.start_time < end_time,
                Booking.end_time > start_time
            )
            .first()
        )
        
        if conflicting_booking:
            return False
        
        # Check availability records
        availability = (
            db.query(Availability)
            .filter(
                Availability.car_id == car_id,
                Availability.start_time <= start_time,
                Availability.end_time >= end_time,
                Availability.status == AvailabilityStatus.AVAILABLE.value
            )
            .first()
        )
        
        # If no availability records, assume available (for simplicity)
        # In production, you might want stricter rules
        return True
    
    @staticmethod
    def create_booking_request(
        db: Session,
        user: User,
        car_id: UUID,
        start_time: datetime,
        end_time: datetime,
        offer_price: Decimal
    ) -> Tuple[Booking, Optional[str]]:
        """
        Create a booking request
        
        Returns: (booking, warning_message)
        Warning message indicates if auction was triggered
        """
        # Check if user should be auto-rejected
        if trust_engine.should_auto_reject(user):
            raise ValueError("Your account is not eligible for bookings at this time.")
        
        # Check basic availability
        car = db.query(Car).filter(Car.id == car_id, Car.is_active == True).first()
        if not car:
            raise ValueError("Car not found or not available.")
        
        # Check for confirmed bookings (hard block)
        confirmed_conflict = (
            db.query(Booking)
            .filter(
                Booking.car_id == car_id,
                Booking.status == BookingStatus.CONFIRMED.value,
                Booking.start_time < end_time,
                Booking.end_time > start_time
            )
            .first()
        )
        
        if confirmed_conflict:
            raise ValueError("Car is already booked for this time period.")
        
        # Create the booking
        booking = Booking(
            user_id=user.id,
            car_id=car_id,
            start_time=start_time,
            end_time=end_time,
            offer_price=offer_price,
            status=BookingStatus.PENDING.value
        )
        db.add(booking)
        db.commit()
        db.refresh(booking)
        
        warning = None
        
        # Check for conflicts with other pending/competing bookings
        conflicts = auction_engine.check_for_conflicts(
            db, car_id, start_time, end_time, exclude_booking_id=booking.id
        )
        
        if conflicts:
            # Trigger auction
            auction, is_new = auction_engine.get_or_create_auction(
                db, car_id, start_time, end_time
            )
            
            # Add all conflicting bookings to auction
            for conflict_booking in conflicts:
                conflict_user = db.query(User).filter(User.id == conflict_booking.user_id).first()
                auction_engine.create_or_update_bid(db, auction, conflict_booking, conflict_user)
            
            # Add current booking to auction
            auction_engine.create_or_update_bid(db, auction, booking, user)
            
            warning = f"Competition detected! Your booking is now in an auction (ID: {auction.id}). Highest trust + offer wins."
        
        db.refresh(booking)
        return booking, warning
    
    @staticmethod
    def cancel_booking(
        db: Session,
        booking: Booking,
        user: User
    ) -> Booking:
        """
        Cancel a booking with potential penalty
        """
        if booking.status not in [BookingStatus.PENDING.value, BookingStatus.COMPETING.value, BookingStatus.CONFIRMED.value]:
            raise ValueError("This booking cannot be cancelled.")
        
        # Check for late cancellation (within 24 hours of start)
        hours_until_start = (booking.start_time - datetime.utcnow()).total_seconds() / 3600
        
        if hours_until_start < 24 and booking.status == BookingStatus.CONFIRMED.value:
            # Apply trust penalty
            trust_engine.apply_cancellation_penalty(db, user)
        
        booking.status = BookingStatus.CANCELLED.value
        booking.updated_at = datetime.utcnow()
        
        db.commit()
        db.refresh(booking)
        return booking
    
    @staticmethod
    def get_user_bookings(
        db: Session,
        user_id: UUID,
        status: Optional[str] = None
    ):
        """Get all bookings for a user"""
        query = db.query(Booking).filter(Booking.user_id == user_id)
        
        if status:
            query = query.filter(Booking.status == status)
        
        return query.order_by(Booking.created_at.desc()).all()


booking_engine = BookingEngine()
