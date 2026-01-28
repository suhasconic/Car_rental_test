"""
In-Memory Data Store
Use this instead of PostgreSQL for development/testing without a database
"""
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import uuid4, UUID
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from app.core.security import get_password_hash


# ============ Data Classes ============

@dataclass
class User:
    id: UUID
    name: str
    email: str
    phone: Optional[str]
    password_hash: str
    role: str = "user"
    total_rides: int = 0
    avg_rating: Decimal = Decimal("0.00")
    damage_count: int = 0
    rash_count: int = 0
    trust_score: Decimal = Decimal("50.00")
    is_blocked: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    @property
    def is_admin(self) -> bool:
        return self.role == "admin"
    
    def calculate_trust_score(self) -> Decimal:
        score = (
            (float(self.avg_rating) * 20) +
            (self.total_rides * 0.5) -
            (self.damage_count * 15) -
            (self.rash_count * 10)
        )
        return Decimal(str(max(score, 0)))


@dataclass
class Car:
    id: UUID
    model: str
    number_plate: str
    daily_price: Decimal
    deposit: Decimal
    image_url: Optional[str] = None
    seats: int = 5
    transmission: str = "automatic"
    fuel_type: str = "petrol"
    description: Optional[str] = None
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Booking:
    id: UUID
    user_id: UUID
    car_id: UUID
    start_time: datetime
    end_time: datetime
    offer_price: Decimal
    status: str = "pending"
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Auction:
    id: UUID
    car_id: UUID
    start_time: datetime
    end_time: datetime
    auction_start: datetime = field(default_factory=datetime.utcnow)
    auction_end: Optional[datetime] = None
    status: str = "active"
    winner_id: Optional[UUID] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Bid:
    id: UUID
    auction_id: UUID
    user_id: UUID
    booking_id: UUID
    offer_price: Decimal
    trust_score_snapshot: Decimal
    final_score: Optional[Decimal] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Ride:
    id: UUID
    booking_id: UUID
    status: str = "active"
    started_at: datetime = field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None


@dataclass
class Rating:
    id: UUID
    ride_id: UUID
    driving_rating: int
    damage_flag: bool = False
    rash_flag: bool = False
    notes: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


# ============ In-Memory Store ============

class InMemoryStore:
    def __init__(self):
        self.users: Dict[UUID, User] = {}
        self.cars: Dict[UUID, Car] = {}
        self.bookings: Dict[UUID, Booking] = {}
        self.auctions: Dict[UUID, Auction] = {}
        self.bids: Dict[UUID, Bid] = {}
        self.rides: Dict[UUID, Ride] = {}
        self.ratings: Dict[UUID, Rating] = {}
        
        # Initialize with seed data
        self._seed_data()
    
    def _seed_data(self):
        """Populate store with initial data"""
        
        # ============ USERS ============
        # Admin user
        admin_id = uuid4()
        self.users[admin_id] = User(
            id=admin_id,
            name="Admin User",
            email="admin@surya.com",
            phone="+91-9876543210",
            password_hash=get_password_hash("admin123"),
            role="admin",
            trust_score=Decimal("100.00")
        )
        
        # Regular users with varying trust scores
        users_data = [
            {
                "name": "Rahul Sharma",
                "email": "rahul@example.com",
                "phone": "+91-9876543211",
                "total_rides": 25,
                "avg_rating": Decimal("4.80"),
                "damage_count": 0,
                "rash_count": 0,
                "trust_score": Decimal("108.50"),  # Excellent driver
            },
            {
                "name": "Priya Patel",
                "email": "priya@example.com",
                "phone": "+91-9876543212",
                "total_rides": 15,
                "avg_rating": Decimal("4.50"),
                "damage_count": 0,
                "rash_count": 1,
                "trust_score": Decimal("87.50"),  # Good driver
            },
            {
                "name": "Amit Singh",
                "email": "amit@example.com",
                "phone": "+91-9876543213",
                "total_rides": 8,
                "avg_rating": Decimal("4.00"),
                "damage_count": 1,
                "rash_count": 0,
                "trust_score": Decimal("69.00"),  # Average driver
            },
            {
                "name": "Neha Gupta",
                "email": "neha@example.com",
                "phone": "+91-9876543214",
                "total_rides": 3,
                "avg_rating": Decimal("3.50"),
                "damage_count": 1,
                "rash_count": 1,
                "trust_score": Decimal("36.50"),  # Below average
            },
            {
                "name": "Vikram Reddy",
                "email": "vikram@example.com",
                "phone": "+91-9876543215",
                "total_rides": 0,
                "avg_rating": Decimal("0.00"),
                "damage_count": 0,
                "rash_count": 0,
                "trust_score": Decimal("50.00"),  # New user
            },
        ]
        
        for data in users_data:
            user_id = uuid4()
            self.users[user_id] = User(
                id=user_id,
                password_hash=get_password_hash("password123"),
                role="user",
                **data
            )
        
        # ============ CARS ============
        cars_data = [
            {
                "model": "Maruti Swift Dzire",
                "number_plate": "KA-01-AB-1234",
                "daily_price": Decimal("1500.00"),
                "deposit": Decimal("5000.00"),
                "seats": 5,
                "transmission": "manual",
                "fuel_type": "petrol",
                "description": "Compact sedan, perfect for city drives. Fuel efficient and easy to handle.",
                "image_url": "https://images.unsplash.com/photo-1549317661-bd32c8ce0db2?w=800"
            },
            {
                "model": "Hyundai Creta",
                "number_plate": "KA-01-CD-5678",
                "daily_price": Decimal("2500.00"),
                "deposit": Decimal("10000.00"),
                "seats": 5,
                "transmission": "automatic",
                "fuel_type": "diesel",
                "description": "Premium SUV with spacious interiors. Great for highway and long trips.",
                "image_url": "https://images.unsplash.com/photo-1606611013016-969c19ba27bb?w=800"
            },
            {
                "model": "Toyota Innova Crysta",
                "number_plate": "KA-01-EF-9012",
                "daily_price": Decimal("3500.00"),
                "deposit": Decimal("15000.00"),
                "seats": 7,
                "transmission": "automatic",
                "fuel_type": "diesel",
                "description": "Luxury MPV with captain seats. Ideal for family trips and airport transfers.",
                "image_url": "https://images.unsplash.com/photo-1619767886558-efdc259cde1a?w=800"
            },
            {
                "model": "Mahindra Thar",
                "number_plate": "KA-01-GH-3456",
                "daily_price": Decimal("3000.00"),
                "deposit": Decimal("12000.00"),
                "seats": 4,
                "transmission": "manual",
                "fuel_type": "diesel",
                "description": "Rugged off-roader for adventure seekers. 4x4 capable with convertible top.",
                "image_url": "https://images.unsplash.com/photo-1609521263047-f8f205293f24?w=800"
            },
            {
                "model": "Honda City",
                "number_plate": "KA-01-IJ-7890",
                "daily_price": Decimal("2000.00"),
                "deposit": Decimal("8000.00"),
                "seats": 5,
                "transmission": "automatic",
                "fuel_type": "petrol",
                "description": "Executive sedan with premium features. Smooth CVT and excellent ride quality.",
                "image_url": "https://images.unsplash.com/photo-1580273916550-e323be2ae537?w=800"
            },
            {
                "model": "Kia Seltos",
                "number_plate": "KA-01-KL-1122",
                "daily_price": Decimal("2200.00"),
                "deposit": Decimal("9000.00"),
                "seats": 5,
                "transmission": "automatic",
                "fuel_type": "petrol",
                "description": "Feature-loaded compact SUV with sunroof and connected car tech.",
                "image_url": "https://images.unsplash.com/photo-1619405399517-d7fce0f13302?w=800"
            },
        ]
        
        for data in cars_data:
            car_id = uuid4()
            self.cars[car_id] = Car(id=car_id, **data)
        
        print("\n✅ In-Memory Store initialized with seed data!")
        print("\n📧 Login Credentials:")
        print("   Admin: admin@surya.com / admin123")
        print("   User:  rahul@example.com / password123")
        print("   User:  priya@example.com / password123")
        print("   User:  amit@example.com / password123")
        print("   User:  neha@example.com / password123")
        print("   User:  vikram@example.com / password123\n")
    
    # ============ User Methods ============
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        for user in self.users.values():
            if user.email == email:
                return user
        return None
    
    def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        return self.users.get(user_id)
    
    def create_user(self, user: User) -> User:
        self.users[user.id] = user
        return user
    
    def get_all_users(self, role: str = None, blocked_only: bool = False) -> List[User]:
        users = list(self.users.values())
        if role:
            users = [u for u in users if u.role == role]
        if blocked_only:
            users = [u for u in users if u.is_blocked]
        return sorted(users, key=lambda u: float(u.trust_score), reverse=True)
    
    # ============ Car Methods ============
    
    def get_car_by_id(self, car_id: UUID) -> Optional[Car]:
        return self.cars.get(car_id)
    
    def get_all_cars(self, active_only: bool = True) -> List[Car]:
        cars = list(self.cars.values())
        if active_only:
            cars = [c for c in cars if c.is_active]
        return cars
    
    def create_car(self, car: Car) -> Car:
        self.cars[car.id] = car
        return car
    
    def update_car(self, car_id: UUID, data: dict) -> Optional[Car]:
        car = self.cars.get(car_id)
        if car:
            for key, value in data.items():
                if hasattr(car, key):
                    setattr(car, key, value)
        return car
    
    def delete_car(self, car_id: UUID) -> bool:
        if car_id in self.cars:
            del self.cars[car_id]
            return True
        return False
    
    # ============ Booking Methods ============
    
    def get_booking_by_id(self, booking_id: UUID) -> Optional[Booking]:
        return self.bookings.get(booking_id)
    
    def get_bookings_by_user(self, user_id: UUID, status: str = None) -> List[Booking]:
        bookings = [b for b in self.bookings.values() if b.user_id == user_id]
        if status:
            bookings = [b for b in bookings if b.status == status]
        return sorted(bookings, key=lambda b: b.created_at, reverse=True)
    
    def get_all_bookings(self, status: str = None) -> List[Booking]:
        bookings = list(self.bookings.values())
        if status:
            bookings = [b for b in bookings if b.status == status]
        return sorted(bookings, key=lambda b: b.created_at, reverse=True)
    
    def create_booking(self, booking: Booking) -> Booking:
        self.bookings[booking.id] = booking
        return booking
    
    def get_conflicting_bookings(self, car_id: UUID, start_time: datetime, end_time: datetime, exclude_id: UUID = None) -> List[Booking]:
        conflicts = []
        for booking in self.bookings.values():
            if booking.car_id == car_id and booking.status in ["pending", "competing"]:
                if booking.start_time < end_time and booking.end_time > start_time:
                    if exclude_id is None or booking.id != exclude_id:
                        conflicts.append(booking)
        return conflicts
    
    # ============ Auction Methods ============
    
    def get_auction_by_id(self, auction_id: UUID) -> Optional[Auction]:
        return self.auctions.get(auction_id)
    
    def get_auctions_by_user(self, user_id: UUID) -> List[Auction]:
        user_auction_ids = set()
        for bid in self.bids.values():
            if bid.user_id == user_id:
                user_auction_ids.add(bid.auction_id)
        return [a for a in self.auctions.values() if a.id in user_auction_ids and a.status == "active"]
    
    def get_all_auctions(self, status: str = None) -> List[Auction]:
        auctions = list(self.auctions.values())
        if status:
            auctions = [a for a in auctions if a.status == status]
        return sorted(auctions, key=lambda a: a.created_at, reverse=True)
    
    def create_auction(self, auction: Auction) -> Auction:
        self.auctions[auction.id] = auction
        return auction
    
    def get_auction_bids(self, auction_id: UUID) -> List[Bid]:
        return [b for b in self.bids.values() if b.auction_id == auction_id]
    
    # ============ Bid Methods ============
    
    def get_bid_by_user_auction(self, user_id: UUID, auction_id: UUID) -> Optional[Bid]:
        for bid in self.bids.values():
            if bid.user_id == user_id and bid.auction_id == auction_id:
                return bid
        return None
    
    def create_bid(self, bid: Bid) -> Bid:
        self.bids[bid.id] = bid
        return bid
    
    # ============ Ride Methods ============
    
    def get_ride_by_booking(self, booking_id: UUID) -> Optional[Ride]:
        for ride in self.rides.values():
            if ride.booking_id == booking_id:
                return ride
        return None
    
    def create_ride(self, ride: Ride) -> Ride:
        self.rides[ride.id] = ride
        return ride
    
    def get_ride_by_id(self, ride_id: UUID) -> Optional[Ride]:
        return self.rides.get(ride_id)
    
    # ============ Rating Methods ============
    
    def get_rating_by_ride(self, ride_id: UUID) -> Optional[Rating]:
        for rating in self.ratings.values():
            if rating.ride_id == ride_id:
                return rating
        return None
    
    def create_rating(self, rating: Rating) -> Rating:
        self.ratings[rating.id] = rating
        return rating


# Global store instance
store = InMemoryStore()
