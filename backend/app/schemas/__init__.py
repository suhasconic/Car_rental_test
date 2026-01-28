# Schemas package
from app.schemas.user import (
    UserCreate,
    UserLogin,
    Token,
    TokenData,
    UserBase,
    UserResponse,
    UserPublic,
    UserUpdate,
)
from app.schemas.car import (
    CarBase,
    CarCreate,
    CarUpdate,
    CarResponse,
    AvailabilityBase,
    AvailabilityCreate,
    AvailabilityResponse,
    CarWithAvailability,
)
from app.schemas.booking import (
    BookingCreate,
    BookingResponse,
    BookingWithDetails,
    RideResponse,
    RideWithBooking,
    RatingCreate,
    RatingResponse,
)
from app.schemas.auction import (
    BidCreate,
    BidResponse,
    BidWithUser,
    AuctionResponse,
    AuctionWithDetails,
    AuctionSummary,
)

__all__ = [
    # User
    "UserCreate",
    "UserLogin", 
    "Token",
    "TokenData",
    "UserBase",
    "UserResponse",
    "UserPublic",
    "UserUpdate",
    # Car
    "CarBase",
    "CarCreate",
    "CarUpdate",
    "CarResponse",
    "AvailabilityBase",
    "AvailabilityCreate",
    "AvailabilityResponse",
    "CarWithAvailability",
    # Booking
    "BookingCreate",
    "BookingResponse",
    "BookingWithDetails",
    "RideResponse",
    "RideWithBooking",
    "RatingCreate",
    "RatingResponse",
    # Auction
    "BidCreate",
    "BidResponse",
    "BidWithUser",
    "AuctionResponse",
    "AuctionWithDetails",
    "AuctionSummary",
]
