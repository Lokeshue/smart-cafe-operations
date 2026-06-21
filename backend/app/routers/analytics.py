"""Analytics and monitoring endpoints."""

import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import AnalyticsDashboardResponse, RushAnalyticsResponse
from app.services.analytics import get_analytics_dashboard
from app.services.queue import RUSH_THRESHOLD, RUSH_WINDOW_MINUTES, detect_rush

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Analytics"])


@router.get("/analytics/rush", response_model=RushAnalyticsResponse)
def get_rush_analytics(db: Session = Depends(get_db)):
    """Check for demand surge in the last 10 minutes."""
    rush_detected, count, message = detect_rush(db)
    return RushAnalyticsResponse(
        rush_detected=rush_detected,
        orders_last_10_minutes=count,
        message=message,
        threshold=RUSH_THRESHOLD,
    )


@router.get("/analytics/dashboard", response_model=AnalyticsDashboardResponse)
def get_dashboard(db: Session = Depends(get_db)):
    """Return monitoring dashboard metrics for store operations."""
    dashboard = get_analytics_dashboard(db)
    logger.info(
        "Dashboard: %d total orders, %d in queue, rush=%s",
        dashboard.total_orders,
        dashboard.active_queue_size,
        dashboard.rush_detected,
    )
    return dashboard
