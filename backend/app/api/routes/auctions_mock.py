from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime
from decimal import Decimal
from fastapi import APIRouter, HTTPException, status, Query, Depends
from pydantic import BaseModel
from app.core.mock_store import store, Booking, Bid
from app.api.routes.auth_mock import get_current_user, User

router = APIRouter(prefix="/auctions", tags=["Auctions"])


# ============ Helpers ============

def auction_to_response(auction, include_bids=True):
    car = store.get_car_by_id(auction.car_id)
    winner = store.get_user_by_id(auction.winner_id) if auction.winner_id else None
    bids = store.get_auction_bids(auction.id) if include_bids else []
    
    bids_response = []
    for bid in bids:
        bid_user = store.get_user_by_id(bid.user_id)
        bids_response.append({
            "id": str(bid.id),
            "auction_id": str(bid.auction_id),
            "user_id": str(bid.user_id),
            "booking_id": str(bid.booking_id),
            "offer_price": float(bid.offer_price),
            "trust_score_snapshot": float(bid.trust_score_snapshot),
            "final_score": float(bid.final_score) if bid.final_score else None,
            "created_at": bid.created_at.isoformat(),
            "user": {
                "id": str(bid_user.id),
                "name": bid_user.name,
                "total_rides": bid_user.total_rides,
                "avg_rating": float(bid_user.avg_rating),
                "trust_score": float(bid_user.trust_score),
                "is_blocked": bid_user.is_blocked,
            } if bid_user else None
        })
    
    highest_bid = max((b.offer_price for b in bids), default=None)
    
    return {
        "id": str(auction.id),
        "car_id": str(auction.car_id),
        "start_time": auction.start_time.isoformat(),
        "end_time": auction.end_time.isoformat(),
        "auction_start": auction.auction_start.isoformat(),
        "auction_end": auction.auction_end.isoformat() if auction.auction_end else None,
        "status": auction.status,
        "winner_id": str(auction.winner_id) if auction.winner_id else None,
        "created_at": auction.created_at.isoformat(),
        "bid_count": len(bids),
        "highest_bid": float(highest_bid) if highest_bid else None,
        "car": {
            "id": str(car.id),
            "model": car.model,
            "number_plate": car.number_plate,
            "daily_price": float(car.daily_price),
            "deposit": float(car.deposit),
            "image_url": car.image_url,
            "seats": car.seats,
            "transmission": car.transmission,
            "fuel_type": car.fuel_type,
        } if car else None,
        "winner": {
            "id": str(winner.id),
            "name": winner.name,
            "trust_score": float(winner.trust_score),
        } if winner else None,
        "bids": bids_response if include_bids else [],
    }


# ============ Routes ============

@router.get("")
def list_auctions(
    status_filter: Optional[str] = Query(None, alias="status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    """List all auctions"""
    auctions = store.get_all_auctions(status_filter)
    auctions = auctions[skip:skip + limit]
    return [auction_to_response(a, include_bids=False) for a in auctions]


@router.get("/my")
def get_my_auctions(current_user: User = Depends(get_current_user)):
    """Get auctions the current user is participating in"""
    auctions = store.get_auctions_by_user(current_user.id)
    return [auction_to_response(a) for a in auctions]


@router.get("/{auction_id}")
def get_auction(
    auction_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get auction details with all bids"""
    try:
        auction = store.get_auction_by_id(UUID(auction_id))
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Auction not found")
    
    if not auction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Auction not found")
    
    return auction_to_response(auction)


@router.post("/{auction_id}/bid")
def place_bid(
    auction_id: str,
    offer_price: float = Query(..., gt=0),
    current_user: User = Depends(get_current_user)
):
    """Place or update a bid on an auction"""
    try:
        auction = store.get_auction_by_id(UUID(auction_id))
    except ValueError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Auction not found")
    
    if not auction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Auction not found")
    
    if auction.status != "active":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This auction is no longer active")
    
    # Check for existing bid
    existing_bid = store.get_bid_by_user_auction(current_user.id, auction.id)
    
    if existing_bid:
        # Update existing bid
        existing_bid.offer_price = Decimal(str(offer_price))
        existing_bid.trust_score_snapshot = current_user.trust_score
        
        # Update associated booking
        booking = store.get_booking_by_id(existing_bid.booking_id)
        if booking:
            booking.offer_price = Decimal(str(offer_price))
        
        return {
            "id": str(existing_bid.id),
            "auction_id": str(existing_bid.auction_id),
            "user_id": str(existing_bid.user_id),
            "offer_price": float(existing_bid.offer_price),
            "trust_score_snapshot": float(existing_bid.trust_score_snapshot),
            "message": "Bid updated successfully"
        }
    else:
        # Create new booking and bid
        booking = Booking(
            id=uuid4(),
            user_id=current_user.id,
            car_id=auction.car_id,
            start_time=auction.start_time,
            end_time=auction.end_time,
            offer_price=Decimal(str(offer_price)),
            status="competing"
        )
        store.create_booking(booking)
        
        bid = Bid(
            id=uuid4(),
            auction_id=auction.id,
            user_id=current_user.id,
            booking_id=booking.id,
            offer_price=Decimal(str(offer_price)),
            trust_score_snapshot=current_user.trust_score
        )
        store.create_bid(bid)
        
        return {
            "id": str(bid.id),
            "auction_id": str(bid.auction_id),
            "user_id": str(bid.user_id),
            "offer_price": float(bid.offer_price),
            "trust_score_snapshot": float(bid.trust_score_snapshot),
            "message": "Bid placed successfully"
        }
