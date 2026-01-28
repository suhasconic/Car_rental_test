from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, Field
from app.schemas.user import UserPublic
from app.schemas.car import CarResponse


# ============ Bid Schemas ============

class BidCreate(BaseModel):
    offer_price: Decimal = Field(..., gt=0)


class BidResponse(BaseModel):
    id: UUID
    auction_id: UUID
    user_id: UUID
    booking_id: UUID
    offer_price: Decimal
    trust_score_snapshot: Decimal
    final_score: Optional[Decimal] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class BidWithUser(BidResponse):
    user: Optional[UserPublic] = None
    
    class Config:
        from_attributes = True


# ============ Auction Schemas ============

class AuctionResponse(BaseModel):
    id: UUID
    car_id: UUID
    start_time: datetime
    end_time: datetime
    auction_start: datetime
    auction_end: Optional[datetime] = None
    status: str
    winner_id: Optional[UUID] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class AuctionWithDetails(AuctionResponse):
    car: Optional[CarResponse] = None
    winner: Optional[UserPublic] = None
    bids: List[BidWithUser] = []
    bid_count: int = 0
    
    class Config:
        from_attributes = True


class AuctionSummary(BaseModel):
    """Summary for auction cards"""
    id: UUID
    car: CarResponse
    start_time: datetime
    end_time: datetime
    status: str
    bid_count: int
    highest_bid: Optional[Decimal] = None
    auction_end: Optional[datetime] = None
    
    class Config:
        from_attributes = True
