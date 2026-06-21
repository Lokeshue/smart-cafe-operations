"""
Smart Café Operations & Nutrition Tracker — FastAPI Backend

REST API for drink customization, nutrition tracking, and smart order queue management.
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routers import analytics, drinks, orders

# Configure logging for important actions
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Smart Café Operations & Nutrition Tracker",
    description="API for Starbucks-style drink customization and smart barista queue management.",
    version="1.0.0",
)

# Allow frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(drinks.router, prefix="/api")
app.include_router(orders.router, prefix="/api")
app.include_router(analytics.router, prefix="/api")


@app.on_event("startup")
def on_startup():
    """Initialize database and seed sample data on first run."""
    init_db()
    logger.info("Smart Café API started successfully.")


@app.get("/")
def root():
    return {
        "message": "Smart Café Operations & Nutrition Tracker API",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
