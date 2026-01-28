import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, String, DateTime, Numeric, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class AvailabilityStatus(str, enum.Enum):
    AVAILABLE = "available"
    LOCKED = "locked"
    BOOKED = "booked"


class BookingStatus(str, enum.Enum):
    PENDING = "pending"
    COMPETING = "competing"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


class Availability(Base):
    __tablename__ = "availability"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    car_id = Column(UUID(as_uuid=True), ForeignKey("cars.id", ondelete="CASCADE"), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    status = Column(String(20), default=AvailabilityStatus.AVAILABLE.value)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    car = relationship("Car", back_populates="availabilities")


class Booking(Base):
    __tablename__ = "bookings"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    car_id = Column(UUID(as_uuid=True), ForeignKey("cars.id", ondelete="CASCADE"), nullable=False)
    
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    offer_price = Column(Numeric(10, 2), nullable=False)
    
    status = Column(String(20), default=BookingStatus.PENDING.value)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="bookings")
    car = relationship("Car", back_populates="bookings")
    bid = relationship("Bid", back_populates="booking", uselist=False)
    ride = relationship("Ride", back_populates="booking", uselist=False)
