"""Order queue management endpoints."""

import json
import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Order
from app.schemas import (
    CustomizeDrinkRequest,
    OrderCreate,
    OrderResponse,
    OrderStatusUpdate,
    QueueStatusResponse,
)
from app.services.nutrition import calculate_nutrition
from app.services.queue import (
    detect_rush,
    get_active_orders,
    order_to_response,
    refresh_queue_priorities,
    sort_queue,
)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Orders"])


@router.post("/orders", response_model=OrderResponse, status_code=201)
def create_order(request: OrderCreate, db: Session = Depends(get_db)):
    """Place a new order and add it to the smart queue."""
    customize_req = CustomizeDrinkRequest(
        drink_id=request.drink_id,
        size=request.size,
        milk_type=request.milk_type,
        vanilla_pumps=request.vanilla_pumps,
        caramel_pumps=request.caramel_pumps,
        mocha_pumps=request.mocha_pumps,
        whipped_cream=request.whipped_cream,
        protein_boost=request.protein_boost,
        extra_espresso_shot=request.extra_espresso_shot,
    )

    try:
        drink, customizations, _ = calculate_nutrition(db, customize_req)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    order = Order(
        customer_name=request.customer_name,
        drink_name=drink.name,
        customizations=json.dumps(customizations),
        channel=request.channel,
        order_time=datetime.utcnow(),
        status="Received",
    )
    db.add(order)
    db.commit()
    db.refresh(order)

    # Recalculate queue priorities after new order
    queue = refresh_queue_priorities(db)
    position = next((i + 1 for i, o in enumerate(queue) if o.id == order.id), None)

    logger.info(
        "New order #%d: %s — %s via %s (queue position #%s)",
        order.id,
        request.customer_name,
        drink.name,
        request.channel,
        position,
    )

    db.refresh(order)
    return OrderResponse(**order_to_response(order, queue_position=position))


@router.get("/orders", response_model=list[OrderResponse])
def list_orders(
    status: str | None = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
):
    """Return all orders, optionally filtered by status."""
    query = db.query(Order)
    if status:
        query = query.filter(Order.status == status)
    orders = query.order_by(Order.order_time.desc()).all()

    active_queue = sort_queue(get_active_orders(db))
    position_map = {o.id: idx + 1 for idx, o in enumerate(active_queue)}

    return [
        OrderResponse(**order_to_response(o, queue_position=position_map.get(o.id)))
        for o in orders
    ]


@router.get("/orders/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    """Get a single order with queue position."""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found.")

    active_queue = sort_queue(get_active_orders(db))
    position = next((i + 1 for i, o in enumerate(active_queue) if o.id == order.id), None)

    return OrderResponse(**order_to_response(order, queue_position=position))


@router.patch("/orders/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: int,
    update: OrderStatusUpdate,
    db: Session = Depends(get_db),
):
    """Update order status (Received → In Progress → Ready → Picked Up)."""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail=f"Order {order_id} not found.")

    valid_transitions = {
        "Received": {"In Progress", "Ready"},
        "In Progress": {"Ready", "Received"},
        "Ready": {"Picked Up", "In Progress"},
        "Picked Up": set(),
    }

    if update.status not in valid_transitions.get(order.status, set()) and update.status != order.status:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot transition from '{order.status}' to '{update.status}'.",
        )

    old_status = order.status
    order.status = update.status
    db.commit()

    logger.info("Order #%d status: %s → %s", order_id, old_status, update.status)

    refresh_queue_priorities(db)
    db.refresh(order)

    active_queue = sort_queue(get_active_orders(db))
    position = next((i + 1 for i, o in enumerate(active_queue) if o.id == order.id), None)

    return OrderResponse(**order_to_response(order, queue_position=position))


@router.get("/queue/status", response_model=QueueStatusResponse)
def get_queue_status(db: Session = Depends(get_db)):
    """
    Return current queue state with smart sequencing and rush alerts.

    Includes queue position and estimated wait for each active order.
    """
    queue = refresh_queue_priorities(db)
    rush_detected, _, rush_message = detect_rush(db)

    avg_wait = 0.0
    if queue:
        now = datetime.utcnow()
        waits = [(now - o.order_time).total_seconds() / 60 for o in queue]
        avg_wait = round(sum(waits) / len(waits), 1)

    orders = [
        OrderResponse(**order_to_response(o, queue_position=idx + 1))
        for idx, o in enumerate(queue)
    ]

    return QueueStatusResponse(
        total_in_queue=len(queue),
        orders=orders,
        rush_detected=rush_detected,
        rush_message=rush_message if rush_detected else None,
        average_wait_minutes=avg_wait,
    )
