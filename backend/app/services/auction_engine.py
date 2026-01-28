from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, List, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.models import Auction, Bid, Booking, User, Availability, AuctionStatus, BookingStatus, AvailabilityStatus
from app.core.config import settings
from app.services.trust_engine import trust_engine


class AuctionEngine:
    """
    Auction Engine
    
    Handles:
    - Creating auctions when booking conflicts occur
    - Converting bookings to bids
    - Calculating final scores
    - Determining winners
    
    Scoring Formula:
    final_score = 0.5 × normalized_trust_score 
                + 0.3 × normalized_rides 
                + 0.2 × normalized_offer_price
    
    Winner Selection:
    - If trust_score >= threshold: highest final_score wins
    - Else: highest offer_price wins (fallback for low-trust bidders)
    """
    
    @staticmethod
    def check_for_conflicts(
        db: Session,
        car_id: UUID,
        start_time: datetime,
        end_time: datetime,
        exclude_booking_id: Optional[UUID] = None
    ) -> List[Booking]:
        """Find overlapping pending/competing bookings for the same car and time"""
        query = (
            db.query(Booking)
            .filter(
                Booking.car_id == car_id,
                Booking.status.in_([BookingStatus.PENDING.value, BookingStatus.COMPETING.value]),
                # Overlap check: (start1 < end2) AND (end1 > start2)
                Booking.start_time < end_time,
                Booking.end_time > start_time
            )
        )
        
        if exclude_booking_id:
            query = query.filter(Booking.id != exclude_booking_id)
        
        return query.all()
    
    @staticmethod
    def get_or_create_auction(
        db: Session,
        car_id: UUID,
        start_time: datetime,
        end_time: datetime
    ) -> Tuple[Auction, bool]:
        """Get existing auction or create new one for the car/time slot"""
        # Check for existing active auction
        existing = (
            db.query(Auction)
            .filter(
                Auction.car_id == car_id,
                Auction.status == AuctionStatus.ACTIVE.value,
                Auction.start_time < end_time,
                Auction.end_time > start_time
            )
            .first()
        )
        
        if existing:
            return existing, False
        
        # Create new auction
        auction_end = datetime.utcnow() + timedelta(hours=settings.AUCTION_DURATION_HOURS)
        auction = Auction(
            car_id=car_id,
            start_time=start_time,
            end_time=end_time,
            auction_end=auction_end,
            status=AuctionStatus.ACTIVE.value
        )
        db.add(auction)
        db.commit()
        db.refresh(auction)
        
        # Lock the availability
        AuctionEngine._lock_availability(db, car_id, start_time, end_time)
        
        return auction, True
    
    @staticmethod
    def _lock_availability(
        db: Session,
        car_id: UUID,
        start_time: datetime,
        end_time: datetime
    ):
        """Lock car availability during auction"""
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
        
        if availability:
            availability.status = AvailabilityStatus.LOCKED.value
            db.commit()
    
    @staticmethod
    def create_or_update_bid(
        db: Session,
        auction: Auction,
        booking: Booking,
        user: User
    ) -> Bid:
        """Create or update a bid for the auction"""
        # Check for existing bid
        existing_bid = (
            db.query(Bid)
            .filter(
                Bid.auction_id == auction.id,
                Bid.user_id == user.id
            )
            .first()
        )
        
        if existing_bid:
            # Update existing bid
            existing_bid.offer_price = booking.offer_price
            existing_bid.trust_score_snapshot = user.trust_score
            existing_bid.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(existing_bid)
            return existing_bid
        
        # Create new bid
        bid = Bid(
            auction_id=auction.id,
            user_id=user.id,
            booking_id=booking.id,
            offer_price=booking.offer_price,
            trust_score_snapshot=user.trust_score
        )
        db.add(bid)
        
        # Update booking status
        booking.status = BookingStatus.COMPETING.value
        
        db.commit()
        db.refresh(bid)
        return bid
    
    @staticmethod
    def calculate_final_scores(db: Session, auction: Auction) -> None:
        """Calculate final scores for all bids in an auction"""
        bids = auction.bids
        if not bids:
            return
        
        # Find max values for normalization
        max_trust = max(float(b.trust_score_snapshot) for b in bids) or 1
        max_rides = max(b.user.total_rides for b in bids) or 1
        max_price = max(float(b.offer_price) for b in bids) or 1
        
        for bid in bids:
            # Normalize components
            normalized_trust = float(bid.trust_score_snapshot) / max_trust
            normalized_rides = bid.user.total_rides / max_rides
            normalized_price = float(bid.offer_price) / max_price
            
            # Calculate final score
            final_score = (
                0.5 * normalized_trust +
                0.3 * normalized_rides +
                0.2 * normalized_price
            )
            
            bid.final_score = Decimal(str(round(final_score, 4)))
        
        db.commit()
    
    @staticmethod
    def determine_winner(db: Session, auction: Auction) -> Optional[Bid]:
        """Determine the winner of an auction"""
        bids = auction.bids
        if not bids:
            return None
        
        # Calculate final scores first
        AuctionEngine.calculate_final_scores(db, auction)
        
        # Separate eligible (high trust) and fallback (low trust) bids
        eligible_bids = [
            b for b in bids 
            if float(b.trust_score_snapshot) >= settings.TRUST_THRESHOLD
        ]
        
        if eligible_bids:
            # Trust-based: highest final_score wins
            winner_bid = max(eligible_bids, key=lambda b: float(b.final_score or 0))
        else:
            # Fallback: highest offer_price wins
            winner_bid = max(bids, key=lambda b: float(b.offer_price))
        
        return winner_bid
    
    @staticmethod
    def close_auction(db: Session, auction: Auction) -> Optional[Booking]:
        """Close an auction and confirm the winning booking"""
        winning_bid = AuctionEngine.determine_winner(db, auction)
        
        if not winning_bid:
            auction.status = AuctionStatus.CLOSED.value
            db.commit()
            return None
        
        # Update auction
        auction.status = AuctionStatus.CLOSED.value
        auction.winner_id = winning_bid.user_id
        auction.auction_end = datetime.utcnow()
        
        # Confirm winning booking
        winning_booking = winning_bid.booking
        winning_booking.status = BookingStatus.CONFIRMED.value
        
        # Reject other bookings
        for bid in auction.bids:
            if bid.id != winning_bid.id:
                bid.booking.status = BookingStatus.REJECTED.value
        
        # Update availability to booked
        availability = (
            db.query(Availability)
            .filter(
                Availability.car_id == auction.car_id,
                Availability.status == AvailabilityStatus.LOCKED.value
            )
            .first()
        )
        if availability:
            availability.status = AvailabilityStatus.BOOKED.value
        
        db.commit()
        return winning_booking
    
    @staticmethod
    def get_user_active_auctions(db: Session, user_id: UUID) -> List[Auction]:
        """Get all active auctions the user is participating in"""
        return (
            db.query(Auction)
            .join(Bid)
            .filter(
                Bid.user_id == user_id,
                Auction.status == AuctionStatus.ACTIVE.value
            )
            .all()
        )


auction_engine = AuctionEngine()
