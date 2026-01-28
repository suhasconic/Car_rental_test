import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, String, Boolean, Integer, DateTime, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base


class Car(Base):
    __tablename__ = "cars"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model = Column(String(100), nullable=False)
    number_plate = Column(String(20), unique=True, nullable=False)
    daily_price = Column(Numeric(10, 2), nullable=False)
    deposit = Column(Numeric(10, 2), nullable=False)
    
    # Additional details
    image_url = Column(String(500), nullable=True)
    seats = Column(Integer, default=5)
    transmission = Column(String(20), default="automatic")  # automatic, manual
    fuel_type = Column(String(20), default="petrol")  # petrol, diesel, electric, hybrid
    description = Column(Text, nullable=True)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    availabilities = relationship("Availability", back_populates="car", cascade="all, delete-orphan")
    bookings = relationship("Booking", back_populates="car", cascade="all, delete-orphan")
    auctions = relationship("Auction", back_populates="car", cascade="all, delete-orphan")
