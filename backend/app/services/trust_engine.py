from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import User, Rating, Ride
from app.core.config import settings


class TrustEngine:
    """
    Trust Score Engine
    
    Calculates and updates user trust scores based on:
    - Average driving rating
    - Total number of rides
    - Damage incidents
    - Rash driving incidents
    
    Formula:
    trust_score = (avg_rating × 20) + (total_rides × 0.5) 
                  - (damage_count × 15) - (rash_count × 10)
    """
    
    @staticmethod
    def calculate_trust_score(
        avg_rating: float,
        total_rides: int,
        damage_count: int,
        rash_count: int
    ) -> Decimal:
        """Calculate trust score from components"""
        score = (
            (avg_rating * 20) +
            (total_rides * 0.5) -
            (damage_count * 15) -
            (rash_count * 10)
        )
        return Decimal(str(max(score, 0)))
    
    @staticmethod
    def recalculate_user_trust(db: Session, user: User) -> User:
        """
        Recalculate user's trust score from their ride history
        """
        # Get all ratings for this user's rides
        ratings = (
            db.query(Rating)
            .join(Ride)
            .join(Ride.booking)
            .filter(Ride.booking.has(user_id=user.id))
            .all()
        )
        
        if ratings:
            # Calculate average rating
            total_rating = sum(r.driving_rating for r in ratings)
            avg_rating = total_rating / len(ratings)
            
            # Count incidents
            damage_count = sum(1 for r in ratings if r.damage_flag)
            rash_count = sum(1 for r in ratings if r.rash_flag)
            
            # Update user stats
            user.total_rides = len(ratings)
            user.avg_rating = Decimal(str(round(avg_rating, 2)))
            user.damage_count = damage_count
            user.rash_count = rash_count
        
        # Calculate new trust score
        user.trust_score = TrustEngine.calculate_trust_score(
            float(user.avg_rating),
            user.total_rides,
            user.damage_count,
            user.rash_count
        )
        
        # Auto-block if below threshold
        if float(user.trust_score) < settings.AUTO_BLOCK_THRESHOLD:
            user.is_blocked = True
        
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def update_after_rating(db: Session, user: User, rating: Rating) -> User:
        """
        Quick update after a new rating is added
        """
        # Increment ride count
        user.total_rides += 1
        
        # Update average rating incrementally
        old_avg = float(user.avg_rating)
        new_avg = ((old_avg * (user.total_rides - 1)) + rating.driving_rating) / user.total_rides
        user.avg_rating = Decimal(str(round(new_avg, 2)))
        
        # Update incident counts
        if rating.damage_flag:
            user.damage_count += 1
        if rating.rash_flag:
            user.rash_count += 1
        
        # Recalculate trust score
        user.trust_score = TrustEngine.calculate_trust_score(
            float(user.avg_rating),
            user.total_rides,
            user.damage_count,
            user.rash_count
        )
        
        # Auto-block check
        if float(user.trust_score) < settings.AUTO_BLOCK_THRESHOLD:
            user.is_blocked = True
        
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def apply_cancellation_penalty(db: Session, user: User) -> User:
        """Apply trust penalty for late cancellation"""
        current_score = float(user.trust_score)
        new_score = max(0, current_score - settings.LATE_CANCEL_PENALTY)
        user.trust_score = Decimal(str(new_score))
        
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def should_auto_reject(user: User) -> bool:
        """Check if user should be auto-rejected"""
        return (
            user.is_blocked or 
            float(user.trust_score) < settings.AUTO_REJECT_THRESHOLD
        )
    
    @staticmethod
    def is_auction_eligible(user: User) -> bool:
        """Check if user is eligible for trust-based auction scoring"""
        return float(user.trust_score) >= settings.TRUST_THRESHOLD


trust_engine = TrustEngine()
