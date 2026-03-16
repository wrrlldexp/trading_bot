import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import Base, engine, SessionLocal
from app.core.demo_data import create_demo_data
from app.routes import strategy, trades, health

# Create tables
Base.metadata.create_all(bind=engine)

# Create demo data if in demo mode
if settings.DEMO_MODE:
    db = SessionLocal()
    try:
        create_demo_data(db)
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage app startup and shutdown."""
    print(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    yield
    print("🛑 Shutting down application")


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(strategy.router)
app.include_router(trades.router)
app.include_router(health.router)


@app.on_event("startup")
async def startup_event():
    """Run on startup."""
    print("✅ Application started")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on shutdown."""
    print("❌ Application stopped")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
