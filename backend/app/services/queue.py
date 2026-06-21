"""Smart queue sequencing and priority scoring service."""

import json
import logging
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models import Order

logger = logging.getLogger(__name__)

ACTIVE_STATUSES = {"Received", "In Progress", "Ready"}
RUSH_THRESHOLD = 12
RUSH_WINDOW_MINUTES = 10
AVG_PREP_MINUTES = 2.5  # Average minutes per drink during normal operations


def compute_priority_score(
    order_time: datetime,
    channel: str,
    drink_name: str,
    active_orders: list[Order],
    now: datetime | None = None,
) -> float:
    """
    Compute priority score for smart queue sequencing.

    Higher score = higher priority.
    Factors:
      - Age: older orders get higher priority
      - Drive-thru boost when average wait exceeds 5 minutes
      - Batch bonus: similar drink already in progress
    """
    now = now or datetime.utcnow()
    wait_minutes = (now - order_time).total_seconds() / 60

    score = wait_minutes * 10  # Base: 10 points per minute waited

    # Drive-thru boost when queue wait is high
    avg_wait = _average_wait(active_orders, now)
    if channel == "drive-thru" and avg_wait >= 5:
        score += 50
        logger.debug("Drive-thru boost applied for %s (avg wait %.1f min)", drink_name, avg_wait)

    # Batch similar drinks: boost if same drink is already being made
    in_progress_drinks = {
        o.drink_name for o in active_orders if o.status == "In Progress"
    }
    if drink_name in in_progress_drinks:
        score += 20

    # Mobile orders get slight boost after 7 min (customer may leave)
    if channel == "mobile" and wait_minutes >= 7:
        score += 15

    return round(score, 2)


def estimate_wait_time(queue_position: int) -> float:
    """Estimate wait time in minutes based on position in queue."""
    return round(max(0, queue_position) * AVG_PREP_MINUTES, 1)


def _average_wait(orders: list[Order], now: datetime) -> float:
    """Calculate average wait time for active orders."""
    if not orders:
        return 0.0
    waits = [(now - o.order_time).total_seconds() / 60 for o in orders]
    return sum(waits) / len(waits)


def get_active_orders(db: Session) -> list[Order]:
    """Fetch all orders that are not yet picked up."""
    return (
        db.query(Order)
        .filter(Order.status.in_(ACTIVE_STATUSES))
        .order_by(Order.priority_score.desc(), Order.order_time.asc())
        .all()
    )


def sort_queue(orders: list[Order]) -> list[Order]:
    """Sort orders by priority score (desc) then order time (asc)."""
    return sorted(orders, key=lambda o: (-o.priority_score, o.order_time))


def detect_rush(db: Session) -> tuple[bool, int, str]:
    """
    Detect demand surge: 12+ orders in the last 10 minutes.

    Returns (rush_detected, order_count, message).
    """
    cutoff = datetime.utcnow() - timedelta(minutes=RUSH_WINDOW_MINUTES)
    count = db.query(Order).filter(Order.order_time >= cutoff).count()

    if count >= RUSH_THRESHOLD:
        message = f"Rush detected: {count} orders in {RUSH_WINDOW_MINUTES} minutes"
        logger.warning(message)
        return True, count, message

    return False, count, f"Normal operations: {count} orders in last {RUSH_WINDOW_MINUTES} minutes"


def order_to_response(order: Order, queue_position: int | None = None) -> dict:
    """Convert Order model to response dict with parsed customizations."""
    return {
        "id": order.id,
        "customer_name": order.customer_name,
        "drink_name": order.drink_name,
        "customizations": json.loads(order.customizations),
        "channel": order.channel,
        "order_time": order.order_time,
        "priority_score": order.priority_score,
        "status": order.status,
        "estimated_wait_minutes": order.estimated_wait_minutes,
        "queue_position": queue_position,
    }


def refresh_queue_priorities(db: Session) -> list[Order]:
    """Recalculate priority scores for all active orders and persist."""
    active = db.query(Order).filter(Order.status.in_(ACTIVE_STATUSES)).all()
    now = datetime.utcnow()
    sorted_queue = sort_queue(active)

    for idx, order in enumerate(sorted_queue):
        order.priority_score = compute_priority_score(
            order_time=order.order_time,
            channel=order.channel,
            drink_name=order.drink_name,
            active_orders=active,
            now=now,
        )
        order.estimated_wait_minutes = estimate_wait_time(idx)

    db.commit()
    return sort_queue(active)
