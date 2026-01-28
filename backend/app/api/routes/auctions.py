from typing import List, Optional
from uuid import UUID
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models import User, Auction, Bid, Booking, AuctionStatus, BookingStatus
from app.schemas import (
    AuctionResponse, AuctionWithDetails, AuctionSummary,
    BidCreate, BidResponse, BidWithUser
)
from app.api.deps import get_current_active_user
from app.services import auction_engine

router = APIRouter(prefix="/auctions", tags=["Auctions"])


@router.get("", response_model=List[AuctionSummary])
def list_auctions(
    status_filter: Optional[str] = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """List all auctions"""
    query = db.query(Auction)
    
    if status_filter:
        query = query.filter(Auction.status == status_filter)
    
    auctions = query.order_by(Auction.created_at.desc()).offset(skip).limit(limit).all()
    
    result = []
    for auction in auctions:
        highest_bid = max((b.offer_price for b in auction.bids), default=None)
        result.append(AuctionSummary(
            id=auction.id,
            car=auction.car,
            start_time=auction.start_time,
            end_time=auction.end_time,
            status=auction.status,
            bid_count=len(auction.bids),
            highest_bid=highest_bid,
            auction_end=auction.auction_end
        ))
    
    return result


@router.get("/my", response_model=List[AuctionWithDetails])
def get_my_auctions(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get auctions the current user is participating in"""
    auctions = auction_engine.get_user_active_auctions(db, current_user.id)
    
    result = []
    for auction in auctions:
        auction_data = AuctionWithDetails(
            id=auction.id,
            car_id=auction.car_id,
            start_time=auction.start_time,
            end_time=auction.end_time,
            auction_start=auction.auction_start,
            auction_end=auction.auction_end,
            status=auction.status,
            winner_id=auction.winner_id,
            created_at=auction.created_at,
            car=auction.car,
            winner=auction.winner,
            bids=auction.bids,
            bid_count=len(auction.bids)
        )
        result.append(auction_data)
    
    return result


@router.get("/{auction_id}", response_model=AuctionWithDetails)
def get_auction(
    auction_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get auction details with all bids"""
    auction = db.query(Auction).filter(Auction.id == auction_id).first()
    
    if not auction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Auction not found"
        )
    
    return AuctionWithDetails(
        id=auction.id,
        car_id=auction.car_id,
        start_time=auction.start_time,
        end_time=auction.end_time,
        auction_start=auction.auction_start,
        auction_end=auction.auction_end,
        status=auction.status,
        winner_id=auction.winner_id,
        created_at=auction.created_at,
        car=auction.car,
        winner=auction.winner,
        bids=auction.bids,
        bid_count=len(auction.bids)
    )


@router.post("/{auction_id}/bid", response_model=BidResponse)
def place_bid(
    auction_id: UUID,
    bid_data: BidCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Place or update a bid on an auction"""
    auction = db.query(Auction).filter(Auction.id == auction_id).first()
    
    if not auction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Auction not found"
        )
    
    if auction.status != AuctionStatus.ACTIVE.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This auction is no longer active"
        )
    
    # Check if user already has a booking for this auction
    existing_bid = (
        db.query(Bid)
        .filter(Bid.auction_id == auction_id, Bid.user_id == current_user.id)
        .first()
    )
    
    if existing_bid:
        # Update existing bid
        existing_bid.offer_price = bid_data.offer_price
        existing_bid.trust_score_snapshot = current_user.trust_score
        
        # Update the associated booking
        existing_bid.booking.offer_price = bid_data.offer_price
        
        db.commit()
        db.refresh(existing_bid)
        return existing_bid
    else:
        # Create a new booking and bid
        booking = Booking(
            user_id=current_user.id,
            car_id=auction.car_id,
            start_time=auction.start_time,
            end_time=auction.end_time,
            offer_price=bid_data.offer_price,
            status=BookingStatus.COMPETING.value
        )
        db.add(booking)
        db.commit()
        db.refresh(booking)
        
        bid = auction_engine.create_or_update_bid(db, auction, booking, current_user)
        return bid
