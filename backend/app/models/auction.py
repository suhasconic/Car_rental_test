import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, String, DateTime, Numeric, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class AuctionStatus(str, enum.Enum):
    ACTIVE = "active"
    CLOSED = "closed"


class Auction(Base):
    __tablename__ = "auctions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    car_id = Column(UUID(as_uuid=True), ForeignKey("cars.id", ondelete="CASCADE"), nullable=False)
    
    # The time period being auctioned
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    
    # Auction lifecycle
    auction_start = Column(DateTime, default=datetime.utcnow)
    auction_end = Column(DateTime, nullable=True)
    
    status = Column(String(20), default=AuctionStatus.ACTIVE.value)
    winner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    car = relationship("Car", back_populates="auctions")
    winner = relationship("User", foreign_keys=[winner_id])
    bids = relationship("Bid", back_populates="auction", cascade="all, delete-orphan")


class Bid(Base):
    __tablename__ = "bids"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    auction_id = Column(UUID(as_uuid=True), ForeignKey("auctions.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    booking_id = Column(UUID(as_uuid=True), ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False)
    
    offer_price = Column(Numeric(10, 2), nullable=False)
    trust_score_snapshot = Column(Numeric(6, 2), nullable=False)
    final_score = Column(Numeric(6, 2), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Unique constraint: one bid per user per auction
    __table_args__ = (
        UniqueConstraint('auction_id', 'user_id', name='unique_user_auction_bid'),
    )
    
    # Relationships
    auction = relationship("Auction", back_populates="bids")
    user = relationship("User", back_populates="bids")
    booking = relationship("Booking", back_populates="bid")
