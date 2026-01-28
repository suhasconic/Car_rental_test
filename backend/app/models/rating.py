import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, Integer, DateTime, Text, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class RideStatus(str, enum.Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    DAMAGED = "damaged"


class Ride(Base):
    __tablename__ = "rides"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    booking_id = Column(UUID(as_uuid=True), ForeignKey("bookings.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    status = Column(String(20), default=RideStatus.ACTIVE.value)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    
    # Relationships
    booking = relationship("Booking", back_populates="ride")
    rating = relationship("Rating", back_populates="ride", uselist=False)


class Rating(Base):
    __tablename__ = "ratings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ride_id = Column(UUID(as_uuid=True), ForeignKey("rides.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    driving_rating = Column(Integer, nullable=False)
    damage_flag = Column(Boolean, default=False)
    rash_flag = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Check constraint for rating range
    __table_args__ = (
        CheckConstraint('driving_rating >= 1 AND driving_rating <= 5', name='rating_range_check'),
    )
    
    # Relationships
    ride = relationship("Ride", back_populates="rating")
