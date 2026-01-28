import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, String, Boolean, Integer, DateTime, Numeric, Text, ForeignKey, CheckConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20), nullable=True)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="user")  # user, admin
    
    # Trust metrics
    total_rides = Column(Integer, default=0)
    avg_rating = Column(Numeric(3, 2), default=Decimal("0.00"))
    damage_count = Column(Integer, default=0)
    rash_count = Column(Integer, default=0)
    trust_score = Column(Numeric(6, 2), default=Decimal("50.00"))
    is_blocked = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    bookings = relationship("Booking", back_populates="user", cascade="all, delete-orphan")
    bids = relationship("Bid", back_populates="user", cascade="all, delete-orphan")
    
    def calculate_trust_score(self) -> Decimal:
        """
        Trust Score Formula:
        trust_score = (avg_rating × 20) + (total_rides × 0.5) 
                      - (damage_count × 15) - (rash_count × 10)
        """
        score = (
            (float(self.avg_rating) * 20) +
            (self.total_rides * 0.5) -
            (self.damage_count * 15) -
            (self.rash_count * 10)
        )
        return Decimal(str(max(score, 0)))
    
    def update_trust_score(self):
        """Recalculate and update trust score"""
        self.trust_score = self.calculate_trust_score()
        
    @property
    def is_admin(self) -> bool:
        return self.role == "admin"
