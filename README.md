# Surya Car Rental - Trust-Weighted Marketplace

A production-grade, two-sided, reputation-driven car rental booking platform with trust-weighted auction system.

![Surya Car Rental](https://images.unsplash.com/photo-1494976388531-d1058494cdd8?w=1200)

## 🎯 Overview

Surya Car Rental is a full-stack marketplace where:
- **Users** can sign up, browse cars, request bookings, and compete in auctions
- **Admins** control fleet, manage approvals, rate drivers, and handle disputes
- **System** automatically manages trust scores, blocks bad drivers, and prioritizes good ones

**Key Innovation**: When multiple users want the same car, a trust-weighted auction determines the winner—not just the highest bidder.

## ✨ Features

### For Users
- 🚗 Browse premium car fleet with filters
- 📅 Request bookings with custom offers
- 🏆 Compete in auctions for high-demand slots
- 📊 Track trust score and reputation
- 📱 Mobile-friendly responsive design

### For Admins
- 📈 Dashboard with real-time stats
- 🚙 Fleet management (add, edit, remove cars)
- ✅ Booking approvals and ride management
- ⭐ Driver rating system with damage/rash flags
- 🔒 User blocking and trust management
- 🔨 Auction control panel

### Trust System
- Dynamic trust scores based on:
  - Average rating (×20)
  - Total rides (×0.5)
  - Damage incidents (×-15)
  - Rash driving flags (×-10)

### Auction Engine
- Automatic auction creation on booking conflicts
- Trust-weighted winner selection
- Fair competition for all users

## 🛠 Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - SQL toolkit and ORM
- **PostgreSQL** - Production database
- **JWT** - Secure authentication
- **Pydantic** - Data validation

### Frontend
- **React 18** - UI library
- **Tailwind CSS** - Utility-first styling
- **Zustand** - State management
- **React Router v6** - Navigation
- **Axios** - HTTP client
- **Lucide Icons** - Beautiful icons

### Infrastructure
- **Docker** - Containerization
- **Docker Compose** - Multi-container orchestration
- **Nginx** - Production web server

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- OR: Python 3.11+, Node.js 18+, PostgreSQL

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd surya-car-rental

# Start all services
docker-compose up --build

# Access the application
# Frontend: http://localhost
# Backend API: http://localhost:8000/api/docs
```

### Option 2: Manual Setup

#### Backend
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up PostgreSQL database
createdb surya_car_rental

# Copy environment file
cp .env.example .env
# Edit .env with your database credentials

# Seed the database
python -m app.seed

# Start the server
uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

## 🔑 Demo Credentials

After seeding the database:

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@surya.com | admin123 |
| User (High Trust) | rahul@example.com | password123 |
| User (Medium Trust) | priya@example.com | password123 |
| User (Low Trust) | neha@example.com | password123 |
| User (New) | vikram@example.com | password123 |

## 📚 API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/signup` | Register new user |
| POST | `/api/auth/login` | Login |
| GET | `/api/cars` | List all cars |
| GET | `/api/cars/{id}` | Car details |
| POST | `/api/bookings/request` | Request booking |
| GET | `/api/bookings/my` | User's bookings |
| GET | `/api/auctions/my` | User's auctions |
| POST | `/api/auctions/{id}/bid` | Place bid |
| POST | `/api/admin/bookings/{id}/approve` | Approve booking |
| POST | `/api/admin/rides/{id}/rate` | Rate driver |

## 🧮 Trust Score Formula

```
trust_score = (avg_rating × 20) + (total_rides × 0.5) - (damage_count × 15) - (rash_count × 10)
```

### Example Calculations:
- New user: 0 × 20 + 0 × 0.5 - 0 × 15 - 0 × 10 = **0** (starts at 50)
- Good driver (4.5★, 20 rides): 4.5 × 20 + 20 × 0.5 = **100**
- Bad driver (3★, 5 rides, 2 damage): 3 × 20 + 5 × 0.5 - 2 × 15 = **32.5**

## 🏆 Auction Scoring

When an auction has multiple bidders:

```
final_score = 0.5 × (trust_score / max_trust) 
            + 0.3 × (rides / max_rides)
            + 0.2 × (offer / max_offer)
```

**Winner Selection**:
- If user's trust ≥ 30: Highest final_score wins
- Otherwise: Highest offer wins (fallback for low-trust users)

## 📁 Project Structure

```
surya-car-rental/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── deps.py          # Auth dependencies
│   │   │   └── routes/          # API routes
│   │   ├── core/
│   │   │   ├── config.py        # Settings
│   │   │   ├── database.py      # DB connection
│   │   │   └── security.py      # JWT & hashing
│   │   ├── models/              # SQLAlchemy models
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── services/
│   │   │   ├── trust_engine.py  # Trust scoring
│   │   │   ├── auction_engine.py # Auction logic
│   │   │   └── booking_engine.py # Booking logic
│   │   ├── main.py              # FastAPI app
│   │   └── seed.py              # Database seeding
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/          # Reusable UI
│   │   ├── pages/               # Route pages
│   │   │   └── admin/           # Admin pages
│   │   ├── services/            # API client
│   │   ├── store/               # Zustand stores
│   │   ├── App.jsx              # Router
│   │   └── index.css            # Tailwind styles
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## 🔒 Security Features

- JWT token authentication
- Password hashing with bcrypt
- Role-based access control
- Protected API routes
- CORS configuration
- SQL injection prevention (SQLAlchemy ORM)

## 🎨 Design Highlights

- **Glassmorphism** UI with blur effects
- **Dark theme** with gradient accents
- **Trust score badges** with color coding
- **Status badges** for bookings/auctions
- **Responsive** mobile-first design
- **Micro-animations** for enhanced UX

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

MIT License - feel free to use for your own projects!

---

Built with ❤️ for modern car rental experiences
