"""Analytics and monitoring service."""

from sqlalchemy.orm import Session

from app.models import Order
from app.schemas import AnalyticsDashboardResponse
from app.services.queue import ACTIVE_STATUSES, detect_rush, get_active_orders


def get_analytics_dashboard(db: Session) -> AnalyticsDashboardResponse:
    """Build analytics dashboard with order metrics and rush status."""
    total_orders = db.query(Order).count()
    active = get_active_orders(db)

    # Average wait for completed + active orders
    from datetime import datetime

    now = datetime.utcnow()
    all_orders = db.query(Order).all()
    if all_orders:
        waits = [(now - o.order_time).total_seconds() / 60 for o in all_orders]
        avg_wait = round(sum(waits) / len(waits), 1)
    else:
        avg_wait = 0.0

    # Orders by channel
    channels = {"mobile": 0, "drive-thru": 0, "walk-in": 0}
    for order in all_orders:
        if order.channel in channels:
            channels[order.channel] += 1

    rush_detected, _, rush_message = detect_rush(db)

    return AnalyticsDashboardResponse(
        total_orders=total_orders,
        average_wait_minutes=avg_wait,
        orders_by_channel=channels,
        rush_detected=rush_detected,
        rush_message=rush_message if rush_detected else None,
        active_queue_size=len(active),
    )
