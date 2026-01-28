"""
Seed script to populate the database with initial data
Run with: python -m app.seed
"""
from datetime import datetime, timedelta
from decimal import Decimal
from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models import User, Car, Availability, AvailabilityStatus


def seed_database():
    db = SessionLocal()
    
    try:
        # Check if already seeded
        if db.query(User).first():
            print("Database already seeded. Skipping...")
            return
        
        print("Seeding database...")
        
        # Create admin user
        admin = User(
            name="Admin User",
            email="admin@surya.com",
            phone="+91-9876543210",
            password_hash=get_password_hash("admin123"),
            role="admin",
            trust_score=Decimal("100.00")
        )
        db.add(admin)
        
        # Create sample users with varying trust scores
        users_data = [
            {
                "name": "Rahul Sharma",
                "email": "rahul@example.com",
                "phone": "+91-9876543211",
                "total_rides": 25,
                "avg_rating": Decimal("4.80"),
                "damage_count": 0,
                "rash_count": 0,
                "trust_score": Decimal("108.50")  # Excellent driver
            },
            {
                "name": "Priya Patel",
                "email": "priya@example.com",
                "phone": "+91-9876543212",
                "total_rides": 15,
                "avg_rating": Decimal("4.50"),
                "damage_count": 0,
                "rash_count": 1,
                "trust_score": Decimal("87.50")  # Good driver
            },
            {
                "name": "Amit Singh",
                "email": "amit@example.com",
                "phone": "+91-9876543213",
                "total_rides": 8,
                "avg_rating": Decimal("4.00"),
                "damage_count": 1,
                "rash_count": 0,
                "trust_score": Decimal("69.00")  # Average driver
            },
            {
                "name": "Neha Gupta",
                "email": "neha@example.com",
                "phone": "+91-9876543214",
                "total_rides": 3,
                "avg_rating": Decimal("3.50"),
                "damage_count": 1,
                "rash_count": 1,
                "trust_score": Decimal("36.50")  # Below average
            },
            {
                "name": "Vikram Reddy",
                "email": "vikram@example.com",
                "phone": "+91-9876543215",
                "total_rides": 0,
                "avg_rating": Decimal("0.00"),
                "damage_count": 0,
                "rash_count": 0,
                "trust_score": Decimal("50.00")  # New user
            }
        ]
        
        for user_data in users_data:
            user = User(
                **user_data,
                password_hash=get_password_hash("password123"),
                role="user"
            )
            db.add(user)
        
        db.commit()
        print(f"Created {len(users_data) + 1} users")
        
        # Create sample cars
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
            }
        ]
        
        for car_data in cars_data:
            car = Car(**car_data, is_active=True)
            db.add(car)
        
        db.commit()
        print(f"Created {len(cars_data)} cars")
        
        # Create availability for all cars (next 30 days)
        cars = db.query(Car).all()
        now = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        for car in cars:
            # Create 30-day availability window
            availability = Availability(
                car_id=car.id,
                start_time=now,
                end_time=now + timedelta(days=30),
                status=AvailabilityStatus.AVAILABLE.value
            )
            db.add(availability)
        
        db.commit()
        print(f"Created availability for {len(cars)} cars")
        
        print("\n✅ Database seeded successfully!")
        print("\n📧 Login credentials:")
        print("   Admin: admin@surya.com / admin123")
        print("   User:  rahul@example.com / password123")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
