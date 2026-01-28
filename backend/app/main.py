from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

# Import routes
from app.api.routes import auth_mock, cars_mock, bookings_mock, auctions_mock, admin_mock

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Trust-weighted car rental marketplace with auction system (In-Memory Mode)",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_mock.router, prefix="/api")
app.include_router(cars_mock.router, prefix="/api")
app.include_router(bookings_mock.router, prefix="/api")
app.include_router(auctions_mock.router, prefix="/api")
app.include_router(admin_mock.router, prefix="/api")


@app.get("/")
def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "mode": "In-Memory (No Database Required)",
        "docs": "/api/docs"
    }


@app.get("/api/health")
def health_check():
    return {"status": "healthy", "mode": "in-memory"}
